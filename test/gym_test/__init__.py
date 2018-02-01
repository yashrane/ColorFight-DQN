import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='Colorfight-v0',
    entry_point='gym_colorfight.envs:ColorFightEnv',
)
