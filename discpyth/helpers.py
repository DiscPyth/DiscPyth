from .structs import Activity, ActivityTypes, UpdateStatusData


def new_update_status_data(  # pylint: disable=too-many-arguments,no-self-use;
    status: str = "online",
    idle: int = 0,
    activity_type=ActivityTypes.GAME,
    name: str = "",
    url: str = "",
):
    if status not in ("online", "dnd", "idle", "invisible"):
        status = "online"
    if name != "":
        act = [Activity(name=name, type=activity_type, url=url)]
    return UpdateStatusData(sinc=idle, status=status, afk=False, activities=act)
