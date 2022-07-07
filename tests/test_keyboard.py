def test_keyboard_on_keypress_in_default_state(keyboard): 
    keyboard.dispatch("ANY_KEY", key='K')
    
    assert keyboard.display == 'k' 

def test_keyboard_on_keypress_in_caps_locked_state(keyboard): 
    keyboard.dispatch('CAPS_LOCK') 
    keyboard.dispatch("ANY_KEY", key='m') 

    assert keyboard.display == 'M'
