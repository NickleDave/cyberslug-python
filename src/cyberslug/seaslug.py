from dataclasses import dataclass
import math


@dataclass
class Position:
    """Position of an agent,
    e.g., a SeaSlug instance."""
    x: int = 0
    y: int = 0
    angle: int = 0


@dataclass
class AntennaPosition:
    """Position of a single sea slug antenna.

    The x and y co-ordinates,
    computed relative to the slug's position
    by the ``SeaSlug.antennae_position`` property.
    """
    x: int
    y: int


@dataclass
class AntennaePositions:
    """Position of the sea slug antennae.

    Position of a single antenna

    Computed relative to the slug's position
    by the ``SeaSlug.antennae_position`` property.
    """
    left: AntennaPosition
    right: AntennaPosition

ODORS = [
    'betaine',
    'flab',
    'hermi',
]

DIRECTIONS = [
    'left',
    'right',
]


@dataclass
class Sensors:
    """Odors of interest smelled by the Cyberslug"""
    betaine_left: float = 0.
    betaine_right: float = 0.
    flab_left: float = 0.
    flab_right: float = 0.
    hermi_left: float = 0.
    hermi_right: float = 0.

    @staticmethod
    def average_odor_strength(self, odor: str):
        left = getattr(self, f'{odor}_left')
        right = getattr(self, f'{odor}_right')
        return (left + right) / 2

    @property
    def betaine(self):
        return self.average_odor_strength('betaine')

    @property
    def flab(self):
        return self.average_odor_strength('flab')

    @property
    def hermi(self):
        return self.average_odor_strength('hermi')



@dataclass
class InternalState:
    """The internal state of the sea slug.

    The attributes of this dataclass are
    the model parameters from et al. 2018.

    Preliminary Rescorla-Wagner parameters for learning Hermi & Flab odors.
    V is learned value of an odor, alpha is the salience
    (or noticeability) of an odor, beta is the learning rate,
    and lambda sets the maximum value of learning (between 0 and 1).

    Attributes
    ----------

    """
    nutrition: float = 0.5
    incentive_salience: float = 0.
    somatic_map: float = 0.
    satiation: float = 0.5
    appetite_switch: int = 0.

    # Rescorla-Wagner parameters for learning
    Vf: float = 0.
    Vh: float = 0.
    alpha_hermi: float = 0.5
    beta_hermi: float = 0.5
    lambda_hermi: float = 1.
    alpha_flab: float = 0.5
    beta_flab: float = 1.
    lambda_flab: float = 1.


class SeaSlug:
    def __init__(self,
                 world,
                 position: Position = Position(),
                 ):
        self.world  # reference to world, to get odors
        self.position = position
        self.sns = Sensors()
        self.state = InternalState()

    def update_sensors(self):
        """Update sensory variables based on odors detected by antennae"""
        for odor in ODORS:
            for direction in DIRECTIONS:
                odor_val = self.world.odor(self.antennae.position)
                if odor_val > 1e-7:
                    sns_val = 7 + math.log10(odor_val)
                else:
                    sns_val = 0
                smell = getattr(self.sns, odor)
                setattr(self.sns, f'{smell}_{direction}', sns_val)

    def somatic_map(self):
        """Transform sensory input into a virtual place code
        of the estimated direction of the strongest odor."""
        F = self.sns.flab - self.sns.hermi
        H = self.sns.hermi - self.sns.flab
        out = (
            # TODO: next line, why negative sign in netlogo code? Don't see in paper
            - (self.sns.flab_left - self.sns.flab_right) / (1 + math.exp(-50. * F)) +
            (self.sns.hermi_left - self.sns.hermi_right) / (1 + math.exp(-50. * H))
        )
        return out

    def update_internal_state(self):
        """Update internal state.

        This method implements the core model from et al. 2018.
        """

        # Nutritional state declines with time
        self.state.nutrition = self.state.nutrition - 0.0005 * self.state.nutrition
        self.state.satiation = 1 / (1 + 0.7 * math.exp(-4  * self.state.nutrition + 2) ** 2)



    def step(self):
        self.update_sensors()
        # self.update_proboscis()  # I think this just draws proboscis
        # not sure if below is "set up" or something we do on every time step?
        # self.set_speed(0.06)
        # self.set_turan_angle()
        self.detect_prey()
