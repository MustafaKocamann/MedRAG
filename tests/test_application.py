import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import application


class ChatTest(unittest.TestCase):
    def setUp(self):
        self.client = application.app.test_client()

    def send(self, prompt):
        return self.client.post(
            "/", data={"prompt": prompt}, headers={"Accept": application.TURN_MEDIA_TYPE}
        )

    def mock_rag(self, *decisions):
        model = Mock()
        model.invoke.side_effect = [SimpleNamespace(content=json.dumps(data)) for data in decisions]
        retriever = Mock()
        retriever.invoke.return_value = [
            SimpleNamespace(
                page_content="The immune system helps the body defend against infection.",
                metadata={"source": "data\\Medical_Reference.pdf", "page": 10},
            )
        ]
        self.enterContext(patch.object(application, "get_model", return_value=model))
        self.enterContext(patch.object(application, "get_retriever", return_value=retriever))
        return retriever

    def test_landing_and_clear(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('lang="tr"', response.text)
        self.assertIn('href="tel:112"', response.text)
        self.assertEqual(self.client.get("/clear").location, "/")

    def test_medication_and_urgent_questions_do_not_call_model(self):
        with patch.object(application, "get_model") as model:
            result = self.send("Hangi antibiyotiği almalıyım?")
            self.assertIn("hekiminize ya da eczacınıza", result.text)
            urgent = self.send("Nefes alamıyorum, hangi ilacı almalıyım?")
            self.assertIn("Acil yardım alın", urgent.text)
            model.assert_not_called()

    def test_approved_answer_renders_escaped_text_and_real_sources(self):
        retriever = self.mock_rag(
            {"status": "answer", "search": "immune system overview"},
            {"status": "answer", "title": "<b>Bağışıklık</b>", "summary": "Savunma sistemidir.",
             "points": ["Enfeksiyonlara karşı korumaya yardımcı olur."]},
            {"status": "answer"},
        )
        result = self.send("<i>Bağışıklık nedir?</i>")
        self.assertEqual(result.mimetype, application.TURN_MEDIA_TYPE)
        self.assertIn("&lt;i&gt;Bağışıklık nedir?&lt;/i&gt;", result.text)
        self.assertIn("<h2>&lt;b&gt;Bağışıklık&lt;/b&gt;</h2>", result.text)
        self.assertIn("<li>Enfeksiyonlara karşı korumaya yardımcı olur.</li>", result.text)
        self.assertIn("Medical Reference · PDF sayfası 11", result.text)
        self.assertNotIn("Set-Cookie", result.headers)
        self.assertEqual(result.headers["Cache-Control"], "no-store")
        retriever.invoke.assert_called_once_with("immune system overview")

    def test_reviewer_blocks_medication_in_candidate(self):
        self.mock_rag(
            {"status": "answer", "search": "immune system overview"},
            {"status": "answer", "title": "İlaç", "summary": "Örnek ilaç talimatı", "points": []},
            {"status": "medication"},
        )
        result = self.send("Bağışıklık sistemi nedir?")
        self.assertIn("hekiminize ya da eczacınıza", result.text)
        self.assertNotIn("Örnek ilaç talimatı", result.text)

    def test_explicit_dose_is_blocked_without_review(self):
        self.mock_rag(
            {"status": "answer", "search": "immune system overview"},
            {"status": "answer", "title": "Bağışıklık", "summary": "25 mg kullanın.", "points": []},
        )
        result = self.send("Bağışıklık nedir?")
        self.assertIn("hekiminize ya da eczacınıza", result.text)
        self.assertNotIn("25 mg", result.text)

    def test_invalid_and_cross_site_requests_stop_before_model(self):
        with patch.object(application, "get_model") as model:
            self.assertEqual(self.send("  ").status_code, 400)
            self.assertEqual(self.send("a" * 1201).status_code, 400)
            result = self.client.post(
                "/", data={"prompt": "Sağlık"}, headers={"Sec-Fetch-Site": "cross-site"}
            )
            self.assertEqual(result.status_code, 403)
            model.assert_not_called()
