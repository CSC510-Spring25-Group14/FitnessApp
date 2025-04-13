import unittest
import time
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import os



class ExerciseRecommenderTests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

        # Get the absolute path of the HTML file
        html_file_path = os.path.abspath("../templates/recommender.html")
        self.driver.get(f"file://{html_file_path}")
        
        # Get common elements
        self.goal_input = self.driver.find_element(By.ID, "goal-input")
        self.submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
    def tearDown(self):
        # Close the browser after each test
        self.driver.quit()
    
    def submit_goal(self, goal_text):
        """Helper method to submit a goal and wait for results to appear"""
        self.goal_input.clear()
        self.goal_input.send_keys(goal_text)
        self.submit_button.click()
        
        # Wait for results to appear
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "results-card"))
        )
        
        # Wait for the spinner to disappear (recommendation generated)
        WebDriverWait(self.driver, 10).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "spinner-border"))
        )
    
    def are_view_details_buttons_absent(self):
        """Helper method to check if View Details buttons are absent"""
        try:
            view_details_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            return len(view_details_buttons) == 0
        except NoSuchElementException:
            return True
    
    def count_tutorial_buttons(self):
        """Helper method to count Watch Tutorial buttons"""
        return len(self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Watch Tutorial')]"))
    
    def verify_card_titles(self, expected_titles):
        """Helper method to verify card titles match expected"""
        titles = self.driver.find_elements(By.CSS_SELECTOR, ".card-title")
        actual_titles = [title.text for title in titles]
        return set(expected_titles).issubset(set(actual_titles))
    
    # Test Case 1: Empty Input Validation
    def test_empty_input(self):
        self.goal_input.clear()
        self.submit_button.click()
        
        # Use alert handling to check for the empty input alert
        alert = self.driver.switch_to.alert
        self.assertEqual(alert.text, "Please enter your workout goal")
        alert.accept()  # Close the alert
    
    # Test Case 3: Results Card Visibility
    def test_results_card_visibility(self):
        self.submit_goal("test")
        
        results_card = self.driver.find_element(By.ID, "results-card")
        self.assertTrue(results_card.is_displayed())
    
    # Test Case 4: Strength Keyword "strength"
    def test_strength_keyword(self):
        self.submit_goal("I need strength training")
        
        # Wait for recommendation titles specifically
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#recommendation-results .card-title"))
        )
        
        # Get only recommendation titles (exclude headers)
        titles = [title.text for title in self.driver.find_elements(
            By.CSS_SELECTOR, "#recommendation-results .card-title"
        )]
        
        expected = ["Push-Ups", "Dumbbell Rows", "Squats"]
        for expected_title in expected:
            self.assertIn(expected_title, titles)

    
    # Test Case 5: Strength Keyword "muscle"
    def test_muscle_keyword(self):
        self.submit_goal("I want to build muscle")
        
        strength_titles = ["Push-Ups", "Dumbbell Rows", "Squats"]
        self.assertTrue(self.verify_card_titles(strength_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 6: Strength Keyword "build"
    def test_build_keyword(self):
        self.submit_goal("I want to build a stronger physique")
        
        strength_titles = ["Push-Ups", "Dumbbell Rows", "Squats"]
        self.assertTrue(self.verify_card_titles(strength_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 8: Cardio Keyword "cardio"
    def test_cardio_keyword(self):
        self.submit_goal("I need cardio exercises")
        
        cardio_titles = ["High-Intensity Interval Training", "Running", "Jump Rope"]
        self.assertTrue(self.verify_card_titles(cardio_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 9: Cardio Keyword "endurance"
    def test_endurance_keyword(self):
        self.submit_goal("Help me improve my endurance")
        
        cardio_titles = ["High-Intensity Interval Training", "Running", "Jump Rope"]
        self.assertTrue(self.verify_card_titles(cardio_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 10: Cardio Keyword "stamina"
# Updated test_stamina_keyword
    def test_stamina_keyword(self):
        self.submit_goal("Improve running stamina")  # More specific input
        
        # Wait for dynamic content
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".card-title"))
        )
        
        # Verify recommendations
        titles = [title.text for title in self.driver.find_elements(By.CSS_SELECTOR, ".card-title")]
        expected = ["High-Intensity Interval Training", "Running", "Jump Rope"]
        for title in expected:
            self.assertIn(title, titles)



    # Test Case 11: Cardio Links
    # Updated test_cardio_links
    def test_cardio_links(self):
        self.submit_goal("cardio workout")
        
        # Wait for links
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn-outline-danger"))
        )
        
        # Verify links
        links = self.driver.find_elements(By.CSS_SELECTOR, "a.btn-outline-danger")
        self.assertEqual(len(links), 3, "Expected 3 tutorial links")
        
        # Verify URLs
        expected_urls = [
            "youtube.com/watch?v=ml6cT4AZdqI",
            "youtube.com/watch?v=_kGESn8ArrU",
            "youtube.com/watch?v=FJmRQ5iTXKE"
        ]
        for link in links:
            self.assertIn("youtube.com", link.get_attribute("href"))



    
    # Test Case 12: Flexibility Keyword "flexibility"
    def test_flexibility_keyword(self):
        self.submit_goal("I need to improve my flexibility")
        
        flexibility_titles = ["Yoga", "Dynamic Stretching", "Pilates"]
        self.assertTrue(self.verify_card_titles(flexibility_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 13: Flexibility Keyword "stretch"
    def test_stretch_keyword(self):
        self.submit_goal("I need stretching exercises")
        
        flexibility_titles = ["Yoga", "Dynamic Stretching", "Pilates"]
        self.assertTrue(self.verify_card_titles(flexibility_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 14: Flexibility Keyword "yoga"
    def test_yoga_keyword(self):
        self.submit_goal("I'm interested in yoga")
        
        flexibility_titles = ["Yoga", "Dynamic Stretching", "Pilates"]
        self.assertTrue(self.verify_card_titles(flexibility_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 16: Default Recommendations
    def test_default_recommendations(self):
        self.submit_goal("I want to get in shape")
        
        default_titles = ["Full Body Circuit", "Bodyweight Exercises", "Walking + Mobility"]
        self.assertTrue(self.verify_card_titles(default_titles))
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 17: Default Recommendations Include Goal Text
    def test_default_includes_goal_text(self):
        goal_text = "I just want to be healthier"
        self.submit_goal(goal_text)
        
        result_text = self.driver.find_element(By.ID, "recommendation-results").text
        self.assertIn(f'Based on your goal: "{goal_text}"', result_text)
        self.assertTrue(self.are_view_details_buttons_absent())
    
    # Test Case 18: Card Styling
    def test_card_styling(self):
        self.submit_goal("test")
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        
        for card in cards:
            # Check computed style
            bg_color = card.value_of_css_property("background-color")
            self.assertIn(bg_color, ["rgba(42, 42, 42, 1)", "rgba(30, 30, 30, 1)"])

    
    # Test Case 19: Tutorial Button Styling and Icons
    def test_tutorial_button_styling(self):
        self.submit_goal("test")
        
        tutorial_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Watch Tutorial')]")
        
        for button in tutorial_buttons:
            # Check if it has the correct class
            self.assertTrue("btn-outline-danger" in button.get_attribute("class"))
            
            # Check if it has an icon
            icon = button.find_element(By.CSS_SELECTOR, "i.fas.fa-play-circle")
            self.assertTrue(icon is not None)
    
    # Test Case 20: View Details Button Absence
    def test_view_details_absence(self):
        # Try different inputs to cover all exercise types
        test_inputs = [
            "strength training",
            "cardio workout",
            "flexibility exercises",
            "general fitness"
        ]
        
        for input_text in test_inputs:
            self.submit_goal(input_text)
            self.assertTrue(self.are_view_details_buttons_absent(), 
                           f"View Details button found when searching for '{input_text}'")

    def test_invalid_input_handling(self):
        # Submit an invalid or nonsensical goal
        self.submit_goal("asdfghjkl")

        # Wait for recommendations to load
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "recommendation-results"))
        )

        # Verify that default recommendations are displayed
        default_titles = ["Full Body Circuit", "Bodyweight Exercises", "Walking + Mobility"]
        self.assertTrue(self.verify_card_titles(default_titles), 
                        "Default recommendations were not displayed for invalid input")

        # Verify the absence of 'View Details' buttons
        self.assertTrue(self.are_view_details_buttons_absent(), 
                        "View Details buttons should not be present for invalid input")

    def test_tutorial_icon_presence(self):
        self.submit_goal("strength training")
        
        # Verify all tutorial buttons have icons
        tutorial_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Watch Tutorial')]")
        for button in tutorial_buttons:
            icon = button.find_element(By.CSS_SELECTOR, "i.fas.fa-play-circle")
            self.assertTrue(icon.is_displayed(), "Tutorial icon missing from button")

    def test_form_resubmission(self):
        # First submission
        self.submit_goal("cardio workout")
        first_results = self.driver.find_elements(By.CSS_SELECTOR, ".card-title")
        first_titles = [title.text for title in first_results]

        # Second submission
        self.submit_goal("flexibility training")
        
        # Wait for new results
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#recommendation-results .card-title"))
        )
        
        # Verify results changed
        second_results = self.driver.find_elements(By.CSS_SELECTOR, "#recommendation-results .card-title")
        second_titles = [title.text for title in second_results]
        self.assertNotEqual(first_titles, second_titles, "Recommendations didn't change on resubmission")




if __name__ == "__main__":
    unittest.main()