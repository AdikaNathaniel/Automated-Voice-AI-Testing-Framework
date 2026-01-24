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
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'poi_type': 'gas_station', 'modifier': 'nearest'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Take me home',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Find parking near downtown',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'location': 'downtown'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'What is the fastest route to work',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'destination': 'work', 'route_preference': 'fastest'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Avoid highways on my route',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'avoid': 'highways'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Show me nearby restaurants',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'poi_type': 'restaurants', 'proximity': 'nearby'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'How long until I arrive',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Cancel navigation',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Find the nearest coffee shop',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'poi_type': 'coffee_shop', 'modifier': 'nearest'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Navigate to 123 Main Street',
            'domain': 'navigation',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
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
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'poi_type': 'gasolinera', 'modifier': 'más_cercana'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Llévame a casa',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Buscar estacionamiento cerca del centro',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'location': 'centro'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Cuál es la ruta más rápida al trabajo',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'destination': 'trabajo', 'route_preference': 'más_rápida'},
                'confidence_threshold': 0.8,
            }
        },
        {
            'query_text': 'Evitar autopistas en mi ruta',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'avoid': 'autopistas'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Mostrar restaurantes cercanos',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'poi_type': 'restaurantes', 'proximity': 'cercanos'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Cuánto tiempo falta para llegar',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Cancelar navegación',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Encontrar la cafetería más cercana',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'poi_type': 'cafetería', 'modifier': 'más_cercana'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Navegar a Avenida Reforma 123',
            'domain': 'navigation',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'NavigationCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
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
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'playlist_name': 'driving'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Play music by The Beatles',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'artist': 'The Beatles'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Skip this song',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Pause the music',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Turn up the volume',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Play some jazz music',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'genre': 'jazz'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'What song is playing',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Repeat this song',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Play the radio',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Shuffle my favorite songs',
            'domain': 'media',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
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
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'playlist_name': 'conducción'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Reproducir música de Los Beatles',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'artist': 'Los Beatles'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Saltar esta canción',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Pausar la música',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Subir el volumen',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Reproducir música de jazz',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'genre': 'jazz'},
                'confidence_threshold': 0.85,
            }
        },
        {
            'query_text': 'Qué canción está sonando',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Repetir esta canción',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Reproducir el radio',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Mezclar mis canciones favoritas',
            'domain': 'media',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'MusicCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
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
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'temperature': 72, 'unit': 'fahrenheit'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Turn on the air conditioning',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Turn on the heater',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Make it warmer',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Make it cooler',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Turn off the AC',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Increase fan speed',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Turn on defrost',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Set climate to auto mode',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'What is the current temperature',
            'domain': 'climate',
            'language': 'en-US',
            'languages': ['en-US'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
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
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {'temperature': 22, 'unit': 'celsius'},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Encender el aire acondicionado',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Encender la calefacción',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Más caliente',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Más frío',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Apagar el aire acondicionado',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Aumentar velocidad del ventilador',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Encender desempañador',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.95,
            }
        },
        {
            'query_text': 'Poner clima en modo automático',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
        {
            'query_text': 'Cuál es la temperatura actual',
            'domain': 'climate',
            'language': 'es-MX',
            'languages': ['es-MX'],
            'expected_command_kind': 'ClimateCommand',
            'expected_outcome': {
                # intent removed (use expected_command_kind)
                'entities': {},
                'confidence_threshold': 0.9,
            }
        },
    ]
}
