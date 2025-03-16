# ai_analysis/tests.py
from django.test import TestCase
from django.urls import reverse

class AIAnalysisTests(TestCase):
    def test_analyze_endpoint(self):
        response = self.client.get(reverse('analyze'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('trend_indicator', data)
        self.assertIn('news_sentiment', data)
        self.assertIn('investment_suggestion', data)

    def test_news_sentiment_endpoint(self):
        response = self.client.get(reverse('news_sentiment'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('news_sentiment', data)

    def test_historical_analysis_endpoint(self):
        response = self.client.get(reverse('historical_analysis'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('trend_indicator', data)
