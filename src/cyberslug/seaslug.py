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
    incentive_salience: int = 0
    somatic_map: int = 0.
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
    def __init__(self, position: Position = Position()):
        self.position = position
        self.travel_history = []
        self.feedcount = {}
        self.sensors = {}
        self.proboscis_extension = 0
        self.state = InternalState()

    @property
    def antennae_positions(self):
        """Antennae are about 40 degrees from the body's lateral axis;
        about 7 units out. 40 degress is about .7 radians.
        """
        left = AntennaPosition(
            x=self.position.x + 7 * math.cos(self.position.angle - .7),
            y=self.position.x + 7 * math.cos(self.position.angle - .7),
        )
        right = AntennaPosition(
            x=self.position.x + 7 * math.cos(self.position.angle + .7),
            y=self.position.x + 7 * math.cos(self.position.angle + .7),
        )

    def update_internal_state(self, n_ticks: int = 1):
        """Update internal state.

        This method implements the core model from et al. 2018.

        Parameters
        ----------
        n_ticks : int
            The number of time steps to advance the model.
            Default is 1.
        """
        # TODO: look at netlogo code here, might be easier to translate?
        # I don't quite follow what's going on with javascript function stuff
        self.state.nutrition *= 0.9995 ** n_ticks
        self.state.satiation = 1 / (1 + 0.7 * math.exp(-4  * self.state.nutrition + 2)) ** 2

        self.state.odor_means = {}
