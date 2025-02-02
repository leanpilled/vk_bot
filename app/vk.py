from models import AttachmentModel
from settings import Settings
from utils import build_request, send_request
from typing import Any
import logging


class VKBotService():
    LONG_POLL_METHOD = "groups.getLongPollServer"
    SEND_MESSAGE_METHOD = "messages.send"
    
    def __init__(
        self,
        settings: Settings,
    ):
        self.__stop = False
        self.__group_id = settings.group_id
        self.__base_vk_api_url = settings.base_vk_api_url
        self.__vk_api_version = settings.vk_api_version
        self.__random_id = settings.random_id
        self.__long_poll_wait = settings.long_poll_wait
        self.__long_poll_server = None
        self.__long_poll_key = None
        self.__long_poll_ts = None
        self.__auth_header = {
            'Authorization': f'Bearer {settings.token}'
        }
        
    def stop_gracefully(self):
        logging.info('gracefully stopping')
        self.__stop = True

    async def __set_long_poll_config(self) -> None:
        logging.info('setting long polling config')
        url = build_request(
            self.__base_vk_api_url,
            self.LONG_POLL_METHOD,
            v=self.__vk_api_version,
            group_id=self.__group_id,
        )
        response = (await send_request(url, self.__auth_header))["response"]
        self.__long_poll_server = response["server"]
        self.__long_poll_key = response["key"]
        self.__long_poll_ts = response["ts"]
    
    def __get_long_poll_url(self) -> str:
        return build_request(
            self.__long_poll_server,
            act="a_check",
            key=self.__long_poll_key,
            ts=self.__long_poll_ts,
            wait=self.__long_poll_wait,
        )

    async def __send_message_with_attachments(
        self,
        peer_id: int,
        message_id: int,
        attachments: list[AttachmentModel],
    ) -> None:
        logging.info(f'sending message with {len(attachments)} attachments to {peer_id}')
        formatted_attachments = ','.join(
            f"photo{attachment.owner_id}_{attachment.media_id}_{attachment.access_key}"
            for attachment in attachments
        )
        url = build_request(
            self.__base_vk_api_url,
            self.SEND_MESSAGE_METHOD,
            v=self.__vk_api_version,
            random_id=self.__random_id,
            user_id=peer_id,
            reply_to=message_id,
            attachment=formatted_attachments,
        )
        response = await send_request(url, self.__auth_header)
        if "error" in response:
            logging.error(
                f"error sending message: {response['error']['error_code']}, {response['error']['error_msg']}"
            )
        
    async def __handle_message(self, data: dict[str, Any]) -> None:
        if "failed" in data:
            error_code = data["failed"]
            if error_code == 1:
                self.__long_poll_ts = data["ts"]
            elif error_code in (2, 3):
                await self.__set_long_poll_config()
        else:
            self.__long_poll_ts = data["ts"]
            for update in data["updates"]:
                if "attachments" in update["object"]["message"]:
                    attachments_to_send = []
                    message = update["object"]["message"]
                    for attachment in message["attachments"]:
                        if attachment["type"] == "photo":
                            attached_photo = attachment["photo"]
                            attachments_to_send.append(
                                AttachmentModel(
                                    owner_id=attached_photo["owner_id"],
                                    media_id=attached_photo["id"],
                                    access_key=attached_photo["access_key"],
                                )
                            )
                    await self.__send_message_with_attachments(
                        message["from_id"],
                        message["id"],
                        attachments_to_send,
                    )

    async def run(self) -> None:
        logging.info('starting up echo bot')
        await self.__set_long_poll_config()
        while True:
            long_poll_url = self.__get_long_poll_url()
            response = await send_request(long_poll_url)
            await self.__handle_message(response)
            if self.__stop:
                break
