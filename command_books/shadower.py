"""A collection of all commands that Adele can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up


# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    HARVEST = "space"

    ROPE_LIFT = "v"
    ERDA_FOUNTAIN = "7"
    
    # 120s Buffs
    MAPLE_GODDESS_BLESSING = ""
    SHADOW_WALKER = ""
    SMOKE_SCREEN = ""
    LAST_RESORT = ""
    TERMS_AND_CONDITIONS = ""

    # 180s buffs
    DECENT_SHARP_EYES = ""
    # TOTEM = "6"

    # 300s+ Buffs
    MAPLE_WARRIOR = ""
    
    # 2 hour familiar juice 
    # JUICE = "4"

    # Skills
    CRUEL_STEP = "shift"
    ASSASSINATE = 'a'
    MESO_EXPLOSION = ""

    SHADOW_ASSAULT = ""
    TRICK_BLADE = ""
    SONIC_BLOW = ""
    SHADOW_FORMATION = ""

    # summons
    DARK_FLARE = ""
    SUDDEN_RAID = ""
    ERDA_FOUNTAIN = "7"


#########################
#       Commands        #
#########################

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.5:
        if direction == 'down':
            press(Key.JUMP, 3)
        elif direction == 'up':
            press(Key.JUMP, 1)
    press(Key.JUMP, num_presses)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.04, 0.05))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.04, 0.05))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        # stop moving
                        time.sleep(utils.rand_float(0.04, 0.05))
                        FlashJump("up").main()
                    else:
                        key_down('down')
                        time.sleep(utils.rand_float(0.04, 0.05))
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(utils.rand_float(0.04, 0.05))
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    def __init__(self):
        super().__init__(locals())
        # self.cd90_buff_time = 0
        self.cd180_buff_time = 0
        self.cd300_buff_time = 0

    def main(self):
        now = time.time()
        is_buff_cast = 0

        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.DECENT_SHARP_EYES, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.cd180_buff_time = now
            is_buff_cast = 1
        if self.cd300_buff_time == 0 or now - self.cd300_buff_time > 300:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.MAPLE_WARRIOR, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.cd300_buff_time = now
            is_buff_cast = 1
        if is_buff_cast:
            time.sleep(utils.rand_float(0.1, 0.12))

class FlashJump(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.JUMP, 2)
        key_up(self.direction)
        time.sleep(utils.rand_float(0.5, 0.6))

# Not tested 
class CruelStep(Command):
    """ Performs Cruel Step attack """
    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(self.direction, 1)
        time.sleep(utils.rand_float(0.04, 0.05))
        press(Key.CRUEL_STEP, 1)
        time.sleep(utils.rand_float(0.15, 0.20))

# Not tested, TODO: more direction combinations
class ShadowAssault(Command):
    """ Performs Shadow Assault attack """
    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        key_down(self.direction)
        time.sleep(utils.rand_float(0.04, 0.05))
        press(Key.CRUEL_STEP, 1)
        time.sleep(utils.rand_float(0.25, 0.30))
        key_up(self.direction) 

class DarkFlare(Command):
     def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(Key.DARK_FLARE, 1)
        time.sleep(utils.rand_float(0.35, 0.40))

class CruelStepMeso(Command):
    """ Performs Cruel Step with meso explosion """
    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        key_down(self.direction)
        CruelStepMesoNoPreDelayNoDirection().main()
        key_up(self.direction)

class CruelStepMesoNoPreDelayNoDirection(Command):
    """ Performs Cruel Step with meso explosion """
    def main(self):
        press(Key.CRUEL_STEP, 1)
        time.sleep(utils.rand_float(0.05, 0.07))
        press(Key.MESO_EXPLOSION, 1)
        time.sleep(utils.rand_float(0.05, 0.10))       

# Not tested 
class Arachnid(Command):
    """Uses 'True Arachnid Reflection' once."""
    def main(self):
        press(Key.ARACHNID, 3)

class JumpAtt(Command):
    """ jump cruel step, only works with two directions: right or left"""
    def __init__(self, direction, attacks_per_jump=1, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks_per_jump)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(self.direction, 1)
        time.sleep(utils.rand_float(0.04, 0.05))
        for _ in range(self.repetitions):
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.04, 0.05))
            for _ in range(self.attacks):
                press(Key.CRUEL_STEP, self.attacks)
                time.sleep(utils.rand_float(0.15, 0.20))
        time.sleep(utils.rand_float(0.05, 0.10))

# Not tested (There is also built in "Fall")
class JumpDownNoDelay(Command):
    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down("down")
        press(Key.JUMP, 1)
        key_up("down")

# Note: There is also built in "Fall"
class JumpDown(Command):
    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down("down")
        press(Key.JUMP, 1)
        key_up("down")
        time.sleep(utils.rand_float(0.1, 0.15))

class JumpDownCruelStepMeso(Command):
    def main(self):
        JumpDownNoDelay().main()
        CruelStepMeso('down').main()

class JumpUpCruelStepMeso(Command):
    def main(self):
        JumpUp().main()
        CruelStepMesoNoPreDelayNoDirection().main()

class FlashJumpAtt(Command):
    """ flash jump cruel step """
    def __init__(self, direction, times=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.times = int(times)

    def main(self):
        key_down(self.direction)
        for _ in range(self.times):
            time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.JUMP, 1, down_time=0.15, up_time=0.05)
            press(Key.JUMP, 1, up_time=0.05) 
            CruelStepMesoNoPreDelayNoDirection().main()
            time.sleep(utils.rand_float(0.1, 0.12))
        key_up(self.direction)


class DoubleFlashJumpAtt(Command):
    """ flash jump twice, cruel step """
    def __init__(self, direction, times=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.times = int(times)

    def main(self):
        key_down(self.direction)
        for _ in range(self.times):
            time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.JUMP, 1, down_time=0.15, up_time=0.05)
            press(Key.JUMP, 2, up_time=0.05) 
            CruelStepMesoNoPreDelayNoDirection().main()
            time.sleep(utils.rand_float(0.1, 0.12))
        key_up(self.direction)

class RopeLift(Command):
    """ Sets up / uses the 5th Job RopeLift skill - direction not affected"""

    def __init__(self):
        super().__init__(locals())

    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.ROPE_LIFT, 2)
        time.sleep(utils.rand_float(0.1, 0.15))

class ErdaFountain(Command):
    def main(self):
        key_down("down")
        time.sleep(utils.rand_float(0.4, 0.5))
        press(Key.ERDA_FOUNTAIN, 1, down_time=0.3)

        key_up("down")
        time.sleep(utils.rand_float(0.1, 0.15))

class JumpUp(Command):
    """ Jumps up"""

    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down("up")
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.03, 0.05))
        press(Key.JUMP, 1)
        key_up("up")
        time.sleep(utils.rand_float(0.1, 0.15))