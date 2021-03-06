###########################################################################
# 
#  Copyright 2019 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from starthinker.manager.log import log_get
from starthinker.ui.recipe.models import Recipe

class Command(BaseCommand):
  help = 'Shows status of recipes'

  def add_arguments(self, parser):
    parser.add_argument(
      '--recipe',
      action='store',
      dest='recipe',
      default=None,
      help='Run a specific recipe.',
    )

  def handle(self, *args, **kwargs):
    #logs = log_get()
    for recipe in (Recipe.objects.filter(pk=kwargs['recipe']) if kwargs['recipe'] else Recipe.objects.all()):
      #recipe.log = logs.get(recipe.uid(), {})
      print recipe.log
      exit()
      print recipe.pk, recipe.uid(), recipe.account.email, recipe.log.get('status'), recipe.log.get('time_ago')
