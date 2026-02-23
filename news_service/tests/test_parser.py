import pytest
from datetime import datetime
from app.services.telegram.parser import MessageParser

class MockMessage:
    def __init__(self, id, text='', message='', photo=None, video=None, document=None, poll=None, venue=None, geo=None, grouped_id=None, views=0, forwards=0, date=None):
        self.id = id
        self.text = text
        self.message = message
        self.photo = photo
        self.video = video
        self.document = document
        self.poll = poll
        self.venue = venue
        self.geo = geo
        self.grouped_id = grouped_id
        self.views = views
        self.forwards = forwards
        self.date = date or datetime.utcnow()

class MockPoll:
    def __init__(self, question):
        self.poll = type('obj', (object,), {'question': question})

def test_parse_simple_text_message():
    msg = MockMessage(id=1, text="Hello World")
    parsed = MessageParser.parse(msg, username="test_chan", title="Test Channel")
    
    assert parsed is not None
    assert parsed['id'] == 1
    assert parsed['channel_username'] == "test_chan"
    assert parsed['text'] == "Hello World"
    assert parsed['has_media'] is False

def test_parse_message_with_empty_text_but_photo():
    msg = MockMessage(id=2, text="", photo=True)
    parsed = MessageParser.parse(msg, username="test_chan", title="Test Channel")
    
    assert parsed is not None
    assert parsed['text'] == "[Media Content]"

def test_parse_message_with_poll():
    msg = MockMessage(id=3, text="", poll=MockPoll("Voting?"))
    parsed = MessageParser.parse(msg, username="test_chan", title="Test Channel")
    
    assert parsed is not None
    assert parsed['text'] == "[Poll: Voting?]"

def test_parse_empty_message_returns_none():
    msg = MockMessage(id=4, text="")
    parsed = MessageParser.parse(msg, username="test_chan", title="Test Channel")
    assert parsed is None

def test_parse_edit_message():
    msg = MockMessage(id=5, text="Edited text")
    parsed = MessageParser.parse(msg, username="test_chan", title="Test Channel", is_edit=True)
    
    assert parsed is not None
    assert parsed['is_edit'] is True
    assert parsed['text'] == "Edited text"
