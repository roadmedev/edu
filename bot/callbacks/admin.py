from aiogram.filters.callback_data import CallbackData


class TeacherAdminCB(CallbackData, prefix="tad"):
    action: str  # view | del | delyes | delno
    teacher_id: int


class CandidateCB(CallbackData, prefix="cand"):
    user_id: int


class StudentAdminCB(CallbackData, prefix="sad"):
    action: str  # view | paid | remind | back
    enrollment_id: int


class TeacherFlowCB(CallbackData, prefix="taf"):
    action: str  # skipcert | cancel