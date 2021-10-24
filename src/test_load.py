import json
import unittest
from unittest.mock import patch, MagicMock

from load import load_url

class Test_load(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_load_url(self, mock_urlopen):
        mock = MagicMock()
        return_raw = {'symbols': 'value'}
        return_value = json.dumps(return_raw)
        mock.read.return_value = return_value.encode('utf8')
        mock.__enter__.return_value = mock
        mock_urlopen.return_value = mock
        result = load_url('https://qwertz', 30)
        assert result == return_raw
        assert result.get('symbols') == 'value'
