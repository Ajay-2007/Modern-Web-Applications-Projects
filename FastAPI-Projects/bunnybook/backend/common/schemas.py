import datetime as dt


from fastapi_camelcase import CamelModel


def dt_to_sio861z(d: dt.datetime) -> str:
    # convert datetime to iso 8601 format, adding milliseconds and "z" suffix
    return f"{d.strftime('%Y-%m-%dT%H:%M:%S:%f')[:-3]}Z"


class BaseSchema(CamelModel):
    # add Zulu timezone to allow javascript correctly parsing UTC timestamps

    class Config:
        json_encoders = {
            dt.datetime: dt_to_sio861z
        }    