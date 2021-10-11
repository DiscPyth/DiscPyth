from . import _Session


class ErrWSAlreadyOpen(Exception):
    def __init__(self, sid) -> None:
        super().__init__(
            f"WebSocket connection already open for shard {sid} no need to reopen"
        )


class ErrWSNotFound(Exception):
    def __init__(self) -> None:
        super().__init__("WebSocket connection connection not found")


class WS_Session:
    def __init__(self, session: _Session) -> None:
        self.__ses: _Session = session

    async def _open(self):

        # This wont be triggered unless the user tries
        # to open the session again at that time we need to raise an
        # error if not then the user may use this multiple times (who knows)
        # and idk what will the side effects be
        if self.__ses.wsConn is not None:
            raise ErrWSAlreadyOpen(self.__ses.ShardID)

    async def _close(self, code=None):
        print("closing")
        if self.__ses.wsConn is not None:

            # default close is 1000 so we dont need to specify
            # that but we need to check if we have a code specified
            if code is not None:
                self.__ses.wsConn.close(code)
            else:
                self.__ses.wsConn.close()
