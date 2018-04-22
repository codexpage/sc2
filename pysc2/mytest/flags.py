from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from absl import app
from absl import flags
from absl import logging

FLAGS = flags.FLAGS

# 1st flags defined
flags.DEFINE_integer('how_many', 3,
                     'specify a small positive integer; for example, 2')

# 2nd flag defined
flags.DEFINE_string('drink', 'beer', 'for example, "soda"')

# number of drinks validator
flags.register_validator(
    'how_many',
    lambda value: 0 < value < 7,
    message='--how_many must be a small positive integer.')


def main(argv):
  # del argv  # Unused.

  # logging to logging.find_log_dir() folder
  version = sys.version_info
  logging.info('Running under Python {0[0]}.{0[1]}.{0[2]}'.format(version))

  # Friday's night!
  for _ in range(FLAGS.how_many):
    print('Drinking %s!' % FLAGS.drink)


if __name__ == '__main__':
  app.run(main)
