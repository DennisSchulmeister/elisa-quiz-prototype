# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__                  import annotations
from bson                        import ObjectId

from ...auth.user                import User
from ...database.analytics.db    import AnalyticsDatabase
from ...database.analytics.types import UserFeedbackData
from ..decorators                import handle_message, websocket_handler
from ..parent                    import ParentWebsocketHandler
from .types                      import PrivacySettingsMessage

@websocket_handler
class AnalyticsHandler:
    """
    Websocket message handler for anonymous usage statistics and anonymous
    user feedback.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent = parent
        self.usage_time_id: ObjectId|None = None
    
    @handle_message("user_feedback", UserFeedbackData)
    async def handle_user_feedback(self, message: UserFeedbackData, user: User, **kwargs):
        """
        Save received anonymous user feedback.
        """
        await AnalyticsDatabase.insert_user_feedback(message, user)
    
    @handle_message("privacy_settings", PrivacySettingsMessage)
    async def handle_privacy_settings(self, privacy: PrivacySettingsMessage, **kwargs):
        """
        Receive privacy settings from client and start recording the application
        usage time, if the user allows. If the consent is revoked, the usage time
        record will be deleted again.
        """
        await self.parent.notify_handlers("record_learning_topics", privacy.record_learning_topics)
        
        if privacy.record_usage_time and not self.usage_time_id:
            # Start recording the usage time
            self.usage_time_id = await AnalyticsDatabase.save_usage_start()
        elif not privacy.record_usage_time and self.usage_time_id:
            # Delete started recording as the user revoked the consent
            await AnalyticsDatabase.delete_usage_time(self.usage_time_id)
            self.usage_time_id = None

    async def on_connection_closed(self):
        """
        Record end of application usage when the connection gets closed and we are
        allowed to track the usage time.
        """
        if self.usage_time_id:
            await AnalyticsDatabase.save_usage_end(self.usage_time_id)