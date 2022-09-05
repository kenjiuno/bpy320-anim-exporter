from typing import Iterable, List, Tuple
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
    frameStart: float
    frameEnd: float

    def __init__(self, pair):
        self.name = pair[0]
        self.frameStart = pair[1].frame_range[0]
        self.frameEnd = pair[1].frame_range[1]
        self.groups = map(lambda it: ActionGroupRef(it),
                          pair[1].groups.items())


def allActions() -> Iterable[ActionRef]:
    return map(lambda it: ActionRef(it), bpy.data.actions.items())


class BoneValue:
    name: str
    parent: int
    translation: List[float]
    rotation: List[float]
    scale: List[float]

    def __init__(self, name, parent, translation, rotation, scale):
        self.name = name
        self.parent = parent
        self.translation = translation
        self.rotation = rotation
        self.scale = scale


def getBoneValues(pairs: List[Tuple]) -> Iterable[BoneValue]:
    boneRefs = list(map(
        lambda it: it[1],
        pairs
    ))

    def indexOfBone(it):
        if it in boneRefs:
            return boneRefs.index(it)
        else:
            return -1

    def getBoneValue(pair: Tuple):
        (translation, rotation, scale) = pair[1].matrix_local.decompose()

        return BoneValue(
            pair[0],
            indexOfBone(pair[1].parent),
            list(translation),
            list(rotation),
            list(scale)
        )

    return map(
        getBoneValue,
        pairs
    )


class RootObjectRef:
    type: str
    name: str
    animationAction: ActionRef
    bones: Iterable[BoneValue]
    fps: float

    def __init__(self, pair):
        self.name = pair[0]
        self.type = pair[1].type
        self.fps = pair[1].users_scene[0].render.fps

        if self.type == 'ARMATURE':
            self.animationAction = ActionRef((
                pair[1].animation_data.action.name,
                pair[1].animation_data.action,
            ))
            self.bones = getBoneValues(pair[1].data.bones.items())
        else:
            self.animationAction = None
            self.bones = None


def allObjects() -> Iterable[RootObjectRef]:
    return map(
        lambda it: RootObjectRef(it),
        bpy.context.collection.all_objects.items()
    )


class AnimExporter:
    def export(self):
        return {
            "version": "1",
            "objects": list(map(
                lambda obj: {
                    "type": obj.type,
                    "name": obj.name,
                    "fps": obj.fps,
                    "animationAction": ({
                        "name": obj.animationAction.name,
                        "frameStart": obj.animationAction.frameStart,
                        "frameEnd": obj.animationAction.frameEnd,
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
                            obj.animationAction.groups
                        ))
                    }) if obj.animationAction else None,
                    "bones": list(map(
                        lambda bone: {
                            "name": bone.name,
                            "parent": bone.parent,
                            "translation": bone.translation,
                            "rotation": bone.rotation,
                            "scale": bone.scale,
                        },
                        obj.bones
                    )) if obj.bones else None,
                },
                allObjects()
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
