from typing import Iterable
import bpy
import json


class HandleValue:
    type: str
    frame: float  # keyTime
    value: float

    def __init__(self, type, frame, value):
        self.type = type
        self.frame = frame
        self.value = value

    def to_dict(self):
        return {
            "type": self.type,
            "frame": self.frame,
            "value": self.value,
        }


class KeyFrameRef:
    type: str  # `KEYFRAME`
    amplitude: float
    easing: str  # `EASE_IN_OUT`
    interpolation: str  # `BEZIER`
    time: float  # keyTime
    value: float
    handleLeft: HandleValue
    handleRight: HandleValue

    def __init__(self, pair):
        self.type = pair[1].type
        self.amplitude = pair[1].amplitude
        self.easing = pair[1].easing
        self.interpolation = pair[1].interpolation
        self.handleLeft = HandleValue(
            pair[1].handle_left_type,
            pair[1].handle_left.x,
            pair[1].handle_left.y
        )
        self.handleRight = HandleValue(
            pair[1].handle_right_type,
            pair[1].handle_right.x,
            pair[1].handle_right.y
        )

        co = pair[1].co
        self.time = co.x
        self.value = co.y


class FCurveRef:
    '''
    `location.0` Tx
    `location.1` Ty
    `location.2` Tz
    `rotation_quaternion.0` Qw
    `rotation_quaternion.1` Qx
    `rotation_quaternion.2` Qy
    `rotation_quaternion.3` Qz
    `scale.0` Sx
    `scale.1` Sy
    `scale.2` Sz
    '''
    channelRef: str
    keyFrames: Iterable[KeyFrameRef]

    def __init__(self, pair):
        self.channelRef = "%s.%d" % (
            pair[1].data_path.split('.')[-1], pair[1].array_index
        )
        self.keyFrames = map(lambda it: KeyFrameRef(it),
                             pair[1].keyframe_points.items())


class ActionGroupRef:
    name: str
    channels: Iterable[FCurveRef]

    def __init__(self, pair):
        self.name = pair[0]
        self.channels = map(lambda it: FCurveRef(it),
                            pair[1].channels.items())


class ActionRef:
    name: str
    groups: Iterable[ActionGroupRef]

    def __init__(self, pair):
        self.name = pair[0]
        self.groups = map(lambda it: ActionGroupRef(it),
                          pair[1].groups.items())


def allActions() -> Iterable[ActionRef]:
    return map(lambda it: ActionRef(it), bpy.data.actions.items())


class AnimExporter:
    def export(self):
        return {
            "actions": list(map(
                lambda action: {
                    "name": action.name,
                    "groups": list(map(
                        lambda group: {
                            "name": group.name,
                            "channels": list(map(
                                lambda channel: {
                                    "channelRef": channel.channelRef,
                                    "keyFrames": list(map(
                                        lambda keyFrame: {
                                            "time": keyFrame.time,
                                            "value": keyFrame.value,
                                            "interpolation": keyFrame.interpolation,
                                            "handleLeft": keyFrame.handleLeft.to_dict(),
                                            "handleRight": keyFrame.handleRight.to_dict(),
                                        },
                                        channel.keyFrames
                                    ))
                                },
                                group.channels
                            ))
                        },
                        action.groups
                    ))
                },
                allActions()
            ))
        }


if False:
    print("running write_some_data...")
    f = open("C:/A/A.json", 'w', encoding='utf-8')
    f.write(
        json.dumps(
            AnimExporter().export(),
            indent=1
        )
    )
    f.close()
