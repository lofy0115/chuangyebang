import pytest
from app.services import NLPService

def test_tokenize():
    service = NLPService()
    words = service.tokenize("这个产品非常好用")
    assert len(words) > 0

def test_sentiment_positive():
    service = NLPService()
    score = service.analyze_sentiment("这个产品非常好用")
    assert score > 0

def test_sentiment_negative():
    service = NLPService()
    score = service.analyze_sentiment("这个产品太差了")
    assert score < 0

def test_classify_complaint():
    service = NLPService()
    # "等了这么久才到" -> 交付问题
    complaint_type = service.classify_complaint("等了这么久才到，拖延太久了")
    assert complaint_type == "交付问题"

def test_classify_price():
    service = NLPService()
    complaint_type = service.classify_complaint("价格太贵了，不划算")
    assert complaint_type == "价格问题"