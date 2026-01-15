from .feed import home_feed, reels_view
from .auth import login_view, logout_view, register_view
from .profile import profile_detail, my_profile, user_profile, profile_edit
from .general import global_premium, explore, notifications
from .groups import GroupListView
from .events import EventListView
from .interactions import toggle_like, add_comment, share_post, delete_post, edit_post, delete_comment
from .api import get_notifications, mark_as_read
from .extras import (
    talkio_app, conscios_view, support_page, settings_page, 
    settings_support, settings_theme, settings_a11y
)
