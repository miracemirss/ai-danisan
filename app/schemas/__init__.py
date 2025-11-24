# app/schemas/__init__.py

from .auth import (
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserLogin,
    UserRead,
)

# ileride clients, sessions vb. için yeni schema dosyaları eklediğinde
# onları da buradan export edebiliriz.
from .appointment import (
    AppointmentBase,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentOut,
    AppointmentStatus
)

from.client import (
    ClientOut,
    ClientCreate,
    ClientBase,
    ClientStatus,
    ClientUpdate
)

from.practitioner import (
    PractitionerProfileCreate,
    Profession,
    PractitionerProfileBase,
    PractitionerProfileOut,
    PractitionerProfileUpdate,
)

from.session import (
    SessionType,
    SessionUpdate,
    SessionBase,
    SessionCreate,
    SessionOut,
)
from.session_note import (
    SessionNoteBase,
    SessionNoteOut,
    SessionNoteCreate,
    SessionNoteUpdate,
    NoteType,
)
from.report import (
    ReportOut,
    ReportBase,
    ReportCreate,
    ReportUpdate,
)

from.subscription_plan import (
    SubscriptionPlanOut,
    SubscriptionPlanBase,
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
)

from.subscription import (
    SubscriptionOut,
    SubscriptionBase,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionStatus,
)

from.ai_job import (
    AiJobOut,
    AiJobBase,
    AiJobType,
    AiJobCreate,
    AiJobUpdate,
    AiJobStatus,
)
from.ai_summary import (
    AiSummaryOut,
    AiSummaryBase,
    AiSummaryCreate,
    AiSummaryUpdate,
)
from.client_consent import (
    ConsentType,
    ClientConsentOut,
    ClientConsentBase,
    ClientConsentCreate,
    ClientConsentUpdate,
)
from.tenant import (
    TenantOut,
    TenantCreate,
    TenantUpdate,
    TenantBase,
)
from.user import (
    UserOut,
    UserUpdate,
    UserBase,
    UserCreate,
    UserPartialUpdate,
)