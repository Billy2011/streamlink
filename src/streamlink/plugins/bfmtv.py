import logging
import re

from streamlink.plugin import Plugin
from streamlink.plugins.brightcove import BrightcovePlayer

log = logging.getLogger(__name__)


class BFMTV(Plugin):
    _url_re = re.compile(r'https://.+\.(?:bfmtv|01net)\.com')
    _dailymotion_url = 'https://www.dailymotion.com/embed/video/{}'
    _brightcove_video_re = re.compile(
        r'accountid="(?P<account_id>[0-9]+).*?videoid="(?P<video_id>[0-9]+)"',
        re.DOTALL
    )
    _brightcove_video_alt_re = re.compile(
        r'data-account="(?P<account_id>[0-9]+).*?data-video-id="(?P<video_id>[0-9]+)"',
        re.DOTALL
    )
    _embed_video_id_re = re.compile(
        r'<iframe.*?src=".*?/(?P<video_id>\w+)"',
        re.DOTALL
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        # Retrieve URL page and search for Brightcove video data
        res = self.session.http.get(self.url)
        match = self._brightcove_video_re.search(res.text) or self._brightcove_video_alt_re.search(res.text)
        if match is not None:
            account_id = match.group('account_id')
            log.debug('Account ID: {0}'.format(account_id))
            video_id = match.group('video_id')
            log.debug('Video ID: {0}'.format(video_id))
            player = BrightcovePlayer(self.session, account_id)
            for stream in player.get_streams(video_id):
                yield stream
        else:
            # Try to find the Dailymotion video ID
            match = self._embed_video_id_re.search(res.text)
            if match is not None:
                video_id = match.group('video_id')
                log.debug('Video ID: {0}'.format(video_id))
                for stream in self.session.streams(self._dailymotion_url.format(video_id)).items():
                    yield stream


__plugin__ = BFMTV
