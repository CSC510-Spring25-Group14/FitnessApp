"""
  Copyright (c) 2025 Hank Lenham, Ryan McPhee, Lawrence Stephenson
  This code is licensed under MIT license (see LICENSE for details)

  @author: Mano Prakash Parthasarathi

  This file tests the functions in utilities.py

  For more information about the Burnout project, visit:
  https://github.com/CSC510-Spring25-Group14/FitnessApp
"""

from utilities import convert_date_to_words, Utilities

def test_get_random_string():
  """
    Test get_random_string function in utilities.py
  """
  random_str_input_length = 8
  random_str = Utilities().get_random_string(length = random_str_input_length)

  assert len(random_str) == random_str_input_length


def test_convert_date_to_words():
  """
    Test convert_date_to_words function in utilities.py
  """
  input_str = "2025-04-07"
  expected_output_words = "April 07, 2025"

  assert convert_date_to_words(input_str) == expected_output_words
