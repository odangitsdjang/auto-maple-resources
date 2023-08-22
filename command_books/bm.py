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
    BLINK_SHOT = "n"
    GRITTY = "q"
    ARROW_BLAST = "d"
    ERDA_FOUNTAIN = "7"
    # 120s Buffs First Rotation
    QUIVER_BARRAGE = "8"
    INHUMAN_SPEED = "0"
    CONCENTRATION = '='

    # 120s Buff Second Rotation (balance out damage)
    STORM_OF_ARROWS = '9'
    EPIC_ADVENTURE = '-'
    VICIOUS_SHOT = "o"

    # TOTEM = "6"

    # 300s+ Buffs
    PHOENIX = "6"
    
    # 2 hour familiar juice 
    # JUICE = "4"

    # Skills
    ARROW_STREAM = "shift"
    HURRICANE = 'a'


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
                        FlashJump("up").main() # Note: Up Jump skill needs to be customized in skill menu to be standard key with other classes
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
    def __init__(self, BlinkShot=False):
        super().__init__(locals())
        # self.cd90_buff_time = 0
        self.cd120_first_rotation = 0
        self.cd120_second_rotation = time.time() - 60
        self.cd300_buff_time = 0
        self.cd60_blinkshot = 0
        self.blink_shot_on = BlinkShot     

    def main(self):
        now = time.time()
        is_buff_cast = 0

        # if self.cd90_buff_time == 0 or now - self.cd120_buff_time > 90:
        #     # press(Key.CONCENTRATION, 2)
        #     # press(Key.VICIOUS_SHOT, 2)
        #     self.cd90_buff_time = now
        
        if self.cd120_first_rotation == 0 or now - self.cd120_first_rotation > 120:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.QUIVER_BARRAGE, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.CONCENTRATION, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.INHUMAN_SPEED, 1)
            time.sleep(utils.rand_float(0.21, 0.25))
            self.cd120_first_rotation = now
            is_buff_cast = 1
        if now - self.cd120_second_rotation > 120:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.STORM_OF_ARROWS, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.EPIC_ADVENTURE, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.VICIOUS_SHOT, 1)
            time.sleep(utils.rand_float(0.21, 0.25))
            self.cd120_second_rotation = now
            is_buff_cast = 1
        if self.cd300_buff_time == 0 or now - self.cd300_buff_time > 300:
            time.sleep(utils.rand_float(0.15, 0.2))
            press(Key.PHOENIX, 1)
            time.sleep(utils.rand_float(0.05, 0.1))
            self.cd300_buff_time = now
            is_buff_cast = 1
        if self.blink_shot_on == "True" and (self.cd60_blinkshot == 0 or now - self.cd60_blinkshot > 60):
            time.sleep(utils.rand_float(0.15, 0.2))
            BlinkShot('up').main()
            BlinkShot('down').main()
            time.sleep(utils.rand_float(0.1, 0.15))
            self.cd60_blinkshot = now
        
        if is_buff_cast:
            time.sleep(utils.rand_float(0.1, 0.12))

class ArrowStream(Command):
    """ Performs Arrow Stream attack """
    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(self.direction, 1)
        time.sleep(utils.rand_float(0.04, 0.05))
        press(Key.ARROW_STREAM, 1)


class ArrowStreamMulti(Command):
    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(self.direction, 1)
        time.sleep(utils.rand_float(0.04, 0.05))
        for _ in range(self.repetitions):
            press(Key.ARROW_STREAM, self.attacks)
            time.sleep(utils.rand_float(0.05, 0.07))
        time.sleep(0.1)


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


class Arachnid(Command):
    """Uses 'True Arachnid Reflection' once."""
    def main(self):
        press(Key.ARACHNID, 3)


class JumpAtt(Command):
    """ jump arrow stream, only works with two directions: right or left"""
    def __init__(self, direction, attacks=2, repetitions=1):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(utils.rand_float(0.04, 0.05))
        press(self.direction, 1)
        time.sleep(utils.rand_float(0.04, 0.05))
        for _ in range(self.repetitions):
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.04, 0.05))
            press(Key.ARROW_STREAM, self.attacks)
            time.sleep(utils.rand_float(0.2, 0.3))
        time.sleep(0.1)

# Timing optimized
class FlashJumpAtt(Command):
    """ flash jump arrow stream, only works with two directions: right or left"""
    def __init__(self, direction, times=1):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.times = int(times)

    def main(self):
        if self.direction != "left" and self.direction != "right":
            return
        
        key_down(self.direction)
        for _ in range(self.times):
            time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.JUMP, 1, down_time=0.15, up_time=0.05)
            press(Key.JUMP, 1, up_time=0.05) 
            press(Key.ARROW_STREAM, 1)
            time.sleep(utils.rand_float(0.398, 0.415))
        key_up(self.direction)


class BlinkShot(Command):
    """ Sets up / uses the Bowmaster Blink Shot TP skill"""
    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.BLINK_SHOT, 2)
        key_up(self.direction)
        time.sleep(utils.rand_float(0.1, 0.15))

class JumpUp(Command):
    """ Jumps up"""

    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.1, 0.15))
        press("up", 1)
        time.sleep(utils.rand_float(0.03, 0.05))
        press("up", 1)
        time.sleep(utils.rand_float(0.1, 0.15))


class RopeLift(Command):
    """ Sets up / uses the 5th Job RopeLift skill - direction not affected"""

    def __init__(self):
        super().__init__(locals())

    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.ROPE_LIFT, 2)
        time.sleep(utils.rand_float(0.1, 0.15))

class GrittyGust(Command):
    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        press(Key.GRITTY, 1)
        time.sleep(utils.rand_float(0.1, 0.15))

# Timing not optimized
class ArrowTurret(Command):
    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        press(self.direction, 1, down_time=0.25)
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down(Key.ARROW_BLAST)
        time.sleep(utils.rand_float(1.2, 1.3))
        press(Key.HARVEST, 1, down_time=0.35)
        press(Key.HARVEST, 1) # press again in case it didnt register before

        key_up(Key.ARROW_BLAST)
        time.sleep(utils.rand_float(0.1, 0.15))

class ErdaFountain(Command):
    def main(self):
        key_down("down")
        time.sleep(utils.rand_float(0.4, 0.5))
        press(Key.ERDA_FOUNTAIN, 1, down_time=0.3)

        key_up("down")
        time.sleep(utils.rand_float(0.1, 0.15))

# Not tested
class ArrowBlasterHold(Command):
    def __init__(self, direction, hold_time_seconds=0):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.hold_time = float(hold_time_seconds)

    def main(self):
        press(self.direction, 1, down_time=0.15)
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down(Key.ARROW_BLAST)
        time.sleep(utils.rand_float(self.hold_time, self.hold_time*1.01))

        key_up(Key.ARROW_BLAST)
        time.sleep(utils.rand_float(0.1, 0.15))

# Not tested
class HurricaneHold(Command):
    def __init__(self, direction, hold_time_seconds=0):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.hold_time = float(hold_time_seconds)

    def main(self):
        press(self.direction, 1, down_time=0.15)
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down(Key.HURRICANE)
        time.sleep(utils.rand_float(self.hold_time, self.hold_time*1.01))

        key_up(Key.HURRICANE)
        time.sleep(utils.rand_float(0.1, 0.15))

# Not tested
class HurricaneKeepHolding(Command):
    def __init__(self, direction, hold_time_seconds=0):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.hold_time = float(hold_time_seconds)

    def main(self):
        press(self.direction, 1, down_time=0.15)
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down(Key.HURRICANE)
        time.sleep(utils.rand_float(self.hold_time, self.hold_time*1.01))

        time.sleep(utils.rand_float(0.1, 0.15))

# Not tested (There is also built in "Fall")
class JumpDownNoDelay(Command):
    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down("down")
        press(Key.JUMP, 1)
        key_up("down")

# Not tested (There is also built in "Fall")
class JumpDown(Command):
    def main(self):
        time.sleep(utils.rand_float(0.1, 0.15))
        key_down("down")
        press(Key.JUMP, 1)
        key_up("down")
        time.sleep(utils.rand_float(0.1, 0.15))

# Not tested
# To be used while HurricaneKeepHolding, after JumpDownNoDelay and before HurricaneRelease
class Spin(Command):
    def __init__(self, direction, hold_time_seconds=0):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.hold_time = float(hold_time_seconds)
        self.start_time = time.time()

    def main(self):
        curr_time = time.time()
        while self.start_time < curr_time - self.hold_time:
            press("left", down_time=0.06, up_time = 0.07)
            press("right", down_time=0.06, up_time = 0.07)
            curr_time = time.time()
        time.sleep(utils.rand_float(0.1, 0.15))

# Not tested
class HurricaneRelease(Command):
    def main(self):
        key_up(Key.HURRICANE)
        time.sleep(utils.rand_float(0.1, 0.15))