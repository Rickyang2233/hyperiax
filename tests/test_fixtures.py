from pytest import fixture
from jaxtrees.tree.builders import THeight_legacy
from jaxtrees.execution import LevelwiseTreeExecutor
from jaxtrees.tree.initializers import initialize_noise_leaves
from jax.random import PRNGKey
from jax import numpy as jnp

@fixture
def small_tree():
    return THeight_legacy(5,2)

@fixture
def noise_tree():
    key = PRNGKey(0)
    t = THeight_legacy(2,2)
    t = initialize_noise_leaves(t,key, (2,))
    return t

@fixture
def phony_executor():
    up = lambda noise, key, params: 2*noise
    down = lambda noise, parent, upmsg, key, params: noise.sqrt()
    fuse = lambda _,points: points.sum(0)

    exe = LevelwiseTreeExecutor(up=up,down=down,fuse=fuse,collate_msgs=jnp.stack, batch_size=20)
    return exe  