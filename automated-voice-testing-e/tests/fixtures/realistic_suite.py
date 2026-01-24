"""
Realistic Test Suite for Pilot Deployment

This suite contains 60 automotive voice AI test cases across:
- 3 domains: navigation (20 cases), media (20 cases), climate (20 cases)
- 2 languages: en-US, es-MX
- Realistic utterances for SoundHound/Houndify automotive integration

TODOS.md Section 7: Pilot readiness - realistic test suite
"""

from datetime import datetime

REALISTIC_SUITE = {
    'name': 'Automotive Voice AI Pilot Suite',
    'description': 'Realistic test suite for automotive voice AI pilot deployment with SoundHound/Houndify',
    'version': '1.0',
    'created_at': datetime.utcnow().isoformat(),
    'domains': ['navigation', 'media', 'climate'],
    'languages': ['en-US', 'es-MX'],
    'test_cases': [
        # NAVIGATION DOMAIN (20 cases)
        # en-US navigation (10 cases)
        {
            'query_text': 'Navigate to the nearest gas station',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'navigate_to_poi',
            'expected_outcome': {
                'intent': 'navigate_to_poi',
                'entities': {'poi_type': 'gas_station', 'modifier': 'nearest'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Take me home',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'navigate_home',
            'expected_outcome': {
                'intent': 'navigate_home',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Find parking near downtown',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'find_parking',
            'expected_outcome': {
                'intent': 'find_parking',
                'entities': {'location': 'downtown'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'What is the fastest route to work',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'get_directions',
            'expected_outcome': {
                'intent': 'get_directions',
                'entities': {'destination': 'work', 'route_preference': 'fastest'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Avoid highways on my route',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'modify_route',
            'expected_outcome': {
                'intent': 'modify_route',
                'entities': {'avoid': 'highways'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Show me nearby restaurants',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'search_poi',
            'expected_outcome': {
                'intent': 'search_poi',
                'entities': {'poi_type': 'restaurants', 'proximity': 'nearby'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'How long until I arrive',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'eta_query',
            'expected_outcome': {
                'intent': 'eta_query',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Cancel navigation',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'cancel_navigation',
            'expected_outcome': {
                'intent': 'cancel_navigation',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Find the nearest coffee shop',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'navigate_to_poi',
            'expected_outcome': {
                'intent': 'navigate_to_poi',
                'entities': {'poi_type': 'coffee_shop', 'modifier': 'nearest'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Navigate to 123 Main Street',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'navigate_to_address',
            'expected_outcome': {
                'intent': 'navigate_to_address',
                'entities': {'address': '123 Main Street'},
                'confidence_threshold': 0.8,
            }
        },

        # es-MX navigation (10 cases)
        {
            'query_text': 'Navegar a la gasolinera más cercana',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'navigate_to_poi',
            'expected_outcome': {
                'intent': 'navigate_to_poi',
                'entities': {'poi_type': 'gasolinera', 'modifier': 'más_cercana'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Llévame a casa',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'navigate_home',
            'expected_outcome': {
                'intent': 'navigate_home',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Buscar estacionamiento cerca del centro',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'find_parking',
            'expected_outcome': {
                'intent': 'find_parking',
                'entities': {'location': 'centro'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Cuál es la ruta más rápida al trabajo',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'get_directions',
            'expected_outcome': {
                'intent': 'get_directions',
                'entities': {'destination': 'trabajo', 'route_preference': 'más_rápida'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Evitar autopistas en mi ruta',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'modify_route',
            'expected_outcome': {
                'intent': 'modify_route',
                'entities': {'avoid': 'autopistas'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Mostrar restaurantes cercanos',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'search_poi',
            'expected_outcome': {
                'intent': 'search_poi',
                'entities': {'poi_type': 'restaurantes', 'proximity': 'cercanos'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Cuánto tiempo falta para llegar',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'eta_query',
            'expected_outcome': {
                'intent': 'eta_query',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Cancelar navegación',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'cancel_navigation',
            'expected_outcome': {
                'intent': 'cancel_navigation',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Encontrar la cafetería más cercana',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'navigate_to_poi',
            'expected_outcome': {
                'intent': 'navigate_to_poi',
                'entities': {'poi_type': 'cafetería', 'modifier': 'más_cercana'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Navegar a Avenida Reforma 123',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'navigate_to_address',
            'expected_outcome': {
                'intent': 'navigate_to_address',
                'entities': {'address': 'Avenida Reforma 123'},
                'confidence_threshold': 0.8,
            }
        },

        # MEDIA DOMAIN (20 cases)
        # en-US media (10 cases)
        {
            'query_text': 'Play my driving playlist',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'play_playlist',
            'expected_outcome': {
                'intent': 'play_playlist',
                'entities': {'playlist_name': 'driving'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Play music by The Beatles',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'play_artist',
            'expected_outcome': {
                'intent': 'play_artist',
                'entities': {'artist': 'The Beatles'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Skip this song',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'skip_track',
            'expected_outcome': {
                'intent': 'skip_track',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Pause the music',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'pause_playback',
            'expected_outcome': {
                'intent': 'pause_playback',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Turn up the volume',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'volume_up',
            'expected_outcome': {
                'intent': 'volume_up',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Play some jazz music',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'play_genre',
            'expected_outcome': {
                'intent': 'play_genre',
                'entities': {'genre': 'jazz'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'What song is playing',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'identify_track',
            'expected_outcome': {
                'intent': 'identify_track',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Repeat this song',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'repeat_track',
            'expected_outcome': {
                'intent': 'repeat_track',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Play the radio',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'play_radio',
            'expected_outcome': {
                'intent': 'play_radio',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Shuffle my favorite songs',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'shuffle_playlist',
            'expected_outcome': {
                'intent': 'shuffle_playlist',
                'entities': {'playlist_type': 'favorites'},
                'confidence_threshold': 0.85,
            }
        },

        # es-MX media (10 cases)
        {
            'query_text': 'Reproducir mi lista de conducción',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'play_playlist',
            'expected_outcome': {
                'intent': 'play_playlist',
                'entities': {'playlist_name': 'conducción'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Reproducir música de Los Beatles',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'play_artist',
            'expected_outcome': {
                'intent': 'play_artist',
                'entities': {'artist': 'Los Beatles'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Saltar esta canción',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'skip_track',
            'expected_outcome': {
                'intent': 'skip_track',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Pausar la música',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'pause_playback',
            'expected_outcome': {
                'intent': 'pause_playback',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Subir el volumen',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'volume_up',
            'expected_outcome': {
                'intent': 'volume_up',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Reproducir música de jazz',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'play_genre',
            'expected_outcome': {
                'intent': 'play_genre',
                'entities': {'genre': 'jazz'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Qué canción está sonando',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'identify_track',
            'expected_outcome': {
                'intent': 'identify_track',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Repetir esta canción',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'repeat_track',
            'expected_outcome': {
                'intent': 'repeat_track',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Reproducir el radio',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'play_radio',
            'expected_outcome': {
                'intent': 'play_radio',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Mezclar mis canciones favoritas',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'shuffle_playlist',
            'expected_outcome': {
                'intent': 'shuffle_playlist',
                'entities': {'playlist_type': 'favoritas'},
                'confidence_threshold': 0.85,
            }
        },

        # CLIMATE DOMAIN (20 cases)
        # en-US climate (10 cases)
        {
            'query_text': 'Set temperature to 72 degrees',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'set_temperature',
            'expected_outcome': {
                'intent': 'set_temperature',
                'entities': {'temperature': 72, 'unit': 'fahrenheit'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Turn on the air conditioning',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'ac_on',
            'expected_outcome': {
                'intent': 'ac_on',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Turn on the heater',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'heat_on',
            'expected_outcome': {
                'intent': 'heat_on',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Make it warmer',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'increase_temperature',
            'expected_outcome': {
                'intent': 'increase_temperature',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Make it cooler',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'decrease_temperature',
            'expected_outcome': {
                'intent': 'decrease_temperature',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Turn off the AC',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'ac_off',
            'expected_outcome': {
                'intent': 'ac_off',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Increase fan speed',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'fan_speed_up',
            'expected_outcome': {
                'intent': 'fan_speed_up',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Turn on defrost',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'defrost_on',
            'expected_outcome': {
                'intent': 'defrost_on',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Set climate to auto mode',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'climate_auto',
            'expected_outcome': {
                'intent': 'climate_auto',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'What is the current temperature',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_intent': 'get_temperature',
            'expected_outcome': {
                'intent': 'get_temperature',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },

        # es-MX climate (10 cases)
        {
            'query_text': 'Ajustar temperatura a 22 grados',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'set_temperature',
            'expected_outcome': {
                'intent': 'set_temperature',
                'entities': {'temperature': 22, 'unit': 'celsius'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Encender el aire acondicionado',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'ac_on',
            'expected_outcome': {
                'intent': 'ac_on',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Encender la calefacción',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'heat_on',
            'expected_outcome': {
                'intent': 'heat_on',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Más caliente',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'increase_temperature',
            'expected_outcome': {
                'intent': 'increase_temperature',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Más frío',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'decrease_temperature',
            'expected_outcome': {
                'intent': 'decrease_temperature',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Apagar el aire acondicionado',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'ac_off',
            'expected_outcome': {
                'intent': 'ac_off',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Aumentar velocidad del ventilador',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'fan_speed_up',
            'expected_outcome': {
                'intent': 'fan_speed_up',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Encender desempañador',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'defrost_on',
            'expected_outcome': {
                'intent': 'defrost_on',
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Poner clima en modo automático',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'climate_auto',
            'expected_outcome': {
                'intent': 'climate_auto',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Cuál es la temperatura actual',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_intent': 'get_temperature',
            'expected_outcome': {
                'intent': 'get_temperature',
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
    ]
}
