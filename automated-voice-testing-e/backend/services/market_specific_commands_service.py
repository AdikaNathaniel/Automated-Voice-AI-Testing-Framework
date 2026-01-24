"""
Market-Specific Commands Service for voice AI testing.

This service provides market-specific voice commands
for different regional automotive markets.

Key features:
- North America market commands
- European markets (per country)
- China, Japan, Korea markets
- Middle East markets
- Command translation and variations

Example:
    >>> service = MarketSpecificCommandsService()
    >>> commands = service.get_na_commands()
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class MarketSpecificCommandsService:
    """
    Service for market-specific voice commands.

    Provides tools for handling regional command variations,
    translations, and market-specific features.

    Example:
        >>> service = MarketSpecificCommandsService()
        >>> config = service.get_market_config()
    """

    def __init__(self):
        """Initialize the market-specific commands service."""
        # North America commands
        self._na_commands = {
            'navigation': ['navigate to', 'take me to', 'directions to', 'find'],
            'climate': ['set temperature to', 'turn on AC', 'turn on heat'],
            'media': ['play music', 'tune to', 'next song', 'previous'],
            'phone': ['call', 'dial', 'text', 'send message'],
            'vehicle': ['open trunk', 'lock doors', 'start car', 'check gas']
        }

        # European command variations by country
        self._eu_commands = {
            'DE': {
                'navigation': ['navigiere zu', 'fahre zu', 'zeige weg zu'],
                'climate': ['stelle temperatur auf', 'klimaanlage ein', 'heizung ein'],
                'media': ['spiele musik', 'naechster titel', 'vorheriger titel']
            },
            'FR': {
                'navigation': ['naviguer vers', 'aller a', 'direction vers'],
                'climate': ['regler temperature', 'climatisation', 'chauffage'],
                'media': ['jouer musique', 'suivant', 'precedent']
            },
            'ES': {
                'navigation': ['navegar a', 'ir a', 'direcciones a'],
                'climate': ['ajustar temperatura', 'aire acondicionado', 'calefaccion'],
                'media': ['reproducir musica', 'siguiente', 'anterior']
            },
            'UK': {
                'navigation': ['navigate to', 'take me to', 'directions to'],
                'climate': ['set temperature', 'air conditioning', 'heating'],
                'media': ['play music', 'next track', 'previous track']
            }
        }

        # Asian market commands
        self._china_commands = {
            'navigation': ['导航到', '带我去', '前往'],
            'climate': ['设置温度', '打开空调', '打开暖气'],
            'media': ['播放音乐', '下一首', '上一首'],
            'phone': ['打电话', '发短信', '拨打']
        }

        self._japan_commands = {
            'navigation': ['案内する', '行く', '道順'],
            'climate': ['温度設定', 'エアコン', '暖房'],
            'media': ['音楽再生', '次の曲', '前の曲'],
            'phone': ['電話する', 'メッセージ', '発信']
        }

        self._korea_commands = {
            'navigation': ['안내', '가다', '길찾기'],
            'climate': ['온도 설정', '에어컨', '히터'],
            'media': ['음악 재생', '다음 곡', '이전 곡'],
            'phone': ['전화', '문자', '통화']
        }

        # Middle East commands
        self._mena_commands = {
            'AR': {
                'navigation': ['انتقل إلى', 'خذني إلى', 'اتجاهات'],
                'climate': ['اضبط درجة الحرارة', 'مكيف الهواء', 'التدفئة'],
                'media': ['تشغيل الموسيقى', 'التالي', 'السابق']
            }
        }

    def get_na_commands(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get North America market commands.

        Args:
            category: Optional category filter

        Returns:
            Dictionary with NA commands

        Example:
            >>> commands = service.get_na_commands('navigation')
        """
        query_id = str(uuid.uuid4())

        if category:
            commands = {category: self._na_commands.get(category, [])}
        else:
            commands = self._na_commands

        return {
            'query_id': query_id,
            'market': 'NA',
            'commands': commands,
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def validate_na_command(
        self,
        command: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate if a command is valid for NA market.

        Args:
            command: Command to validate
            category: Optional category to check

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_na_command('navigate to')
        """
        validation_id = str(uuid.uuid4())

        command_lower = command.lower()
        found_in = []

        categories_to_check = [category] if category else self._na_commands.keys()

        for cat in categories_to_check:
            if cat in self._na_commands:
                for cmd in self._na_commands[cat]:
                    if cmd in command_lower or command_lower in cmd:
                        found_in.append(cat)
                        break

        return {
            'validation_id': validation_id,
            'command': command,
            'valid': len(found_in) > 0,
            'found_in_categories': found_in,
            'market': 'NA',
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_eu_commands(
        self,
        country_code: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get European market commands.

        Args:
            country_code: Optional country code (DE, FR, ES, UK)
            category: Optional category filter

        Returns:
            Dictionary with EU commands

        Example:
            >>> commands = service.get_eu_commands('DE', 'navigation')
        """
        query_id = str(uuid.uuid4())

        if country_code:
            country_commands = self._eu_commands.get(country_code, {})
            if category:
                commands = {country_code: {category: country_commands.get(category, [])}}
            else:
                commands = {country_code: country_commands}
        else:
            commands = self._eu_commands

        return {
            'query_id': query_id,
            'market': 'EU',
            'country_code': country_code,
            'commands': commands,
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_country_specific_commands(
        self,
        country_code: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get commands for a specific country.

        Args:
            country_code: Country code
            categories: Optional list of categories

        Returns:
            Dictionary with country commands

        Example:
            >>> commands = service.get_country_specific_commands('DE')
        """
        query_id = str(uuid.uuid4())

        # Find country in all markets
        commands = {}

        if country_code in ['US', 'CA', 'MX']:
            commands = self._na_commands
            market = 'NA'
        elif country_code in self._eu_commands:
            commands = self._eu_commands[country_code]
            market = 'EU'
        elif country_code == 'CN':
            commands = self._china_commands
            market = 'APAC'
        elif country_code == 'JP':
            commands = self._japan_commands
            market = 'APAC'
        elif country_code == 'KR':
            commands = self._korea_commands
            market = 'APAC'
        elif country_code in self._mena_commands:
            commands = self._mena_commands[country_code]
            market = 'MENA'
        else:
            market = 'unknown'

        if categories:
            commands = {k: v for k, v in commands.items() if k in categories}

        return {
            'query_id': query_id,
            'country_code': country_code,
            'market': market,
            'commands': commands,
            'categories_filtered': categories,
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_china_commands(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get China market commands.

        Args:
            category: Optional category filter

        Returns:
            Dictionary with China commands

        Example:
            >>> commands = service.get_china_commands()
        """
        query_id = str(uuid.uuid4())

        if category:
            commands = {category: self._china_commands.get(category, [])}
        else:
            commands = self._china_commands

        return {
            'query_id': query_id,
            'market': 'CN',
            'commands': commands,
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_japan_commands(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Japan market commands.

        Args:
            category: Optional category filter

        Returns:
            Dictionary with Japan commands

        Example:
            >>> commands = service.get_japan_commands()
        """
        query_id = str(uuid.uuid4())

        if category:
            commands = {category: self._japan_commands.get(category, [])}
        else:
            commands = self._japan_commands

        return {
            'query_id': query_id,
            'market': 'JP',
            'commands': commands,
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_korea_commands(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Korea market commands.

        Args:
            category: Optional category filter

        Returns:
            Dictionary with Korea commands

        Example:
            >>> commands = service.get_korea_commands()
        """
        query_id = str(uuid.uuid4())

        if category:
            commands = {category: self._korea_commands.get(category, [])}
        else:
            commands = self._korea_commands

        return {
            'query_id': query_id,
            'market': 'KR',
            'commands': commands,
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_mena_commands(
        self,
        country_code: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Middle East and North Africa market commands.

        Args:
            country_code: Optional country code
            category: Optional category filter

        Returns:
            Dictionary with MENA commands

        Example:
            >>> commands = service.get_mena_commands('AR')
        """
        query_id = str(uuid.uuid4())

        if country_code:
            country_commands = self._mena_commands.get(country_code, {})
            if category:
                commands = {country_code: {category: country_commands.get(category, [])}}
            else:
                commands = {country_code: country_commands}
        else:
            commands = self._mena_commands

        return {
            'query_id': query_id,
            'market': 'MENA',
            'country_code': country_code,
            'commands': commands,
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def translate_command(
        self,
        command: str,
        source_market: str,
        target_market: str
    ) -> Dict[str, Any]:
        """
        Translate command between markets.

        Args:
            command: Command to translate
            source_market: Source market code
            target_market: Target market code

        Returns:
            Dictionary with translation result

        Example:
            >>> result = service.translate_command('navigate to', 'NA', 'DE')
        """
        translation_id = str(uuid.uuid4())

        # Find category in source market
        source_category = None
        command_lower = command.lower()

        if source_market in ['US', 'NA']:
            for cat, cmds in self._na_commands.items():
                for cmd in cmds:
                    if cmd in command_lower:
                        source_category = cat
                        break

        # Get equivalent in target market
        translated = command
        if source_category:
            if target_market in self._eu_commands:
                target_cmds = self._eu_commands[target_market].get(source_category, [])
                if target_cmds:
                    translated = target_cmds[0]
            elif target_market == 'CN':
                target_cmds = self._china_commands.get(source_category, [])
                if target_cmds:
                    translated = target_cmds[0]
            elif target_market == 'JP':
                target_cmds = self._japan_commands.get(source_category, [])
                if target_cmds:
                    translated = target_cmds[0]

        return {
            'translation_id': translation_id,
            'original_command': command,
            'translated_command': translated,
            'source_market': source_market,
            'target_market': target_market,
            'category': source_category,
            'translated_at': datetime.utcnow().isoformat()
        }

    def get_command_variations(
        self,
        base_command: str,
        markets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get command variations across markets.

        Args:
            base_command: Base command to find variations for
            markets: Optional list of markets to check

        Returns:
            Dictionary with command variations

        Example:
            >>> variations = service.get_command_variations('navigate to')
        """
        query_id = str(uuid.uuid4())

        variations = {}
        command_lower = base_command.lower()

        # Find category
        category = None
        for cat, cmds in self._na_commands.items():
            for cmd in cmds:
                if cmd in command_lower:
                    category = cat
                    break

        if category:
            all_markets = markets or ['NA', 'DE', 'FR', 'ES', 'CN', 'JP', 'KR']

            for market in all_markets:
                if market == 'NA':
                    variations['NA'] = self._na_commands.get(category, [])
                elif market in self._eu_commands:
                    variations[market] = self._eu_commands[market].get(category, [])
                elif market == 'CN':
                    variations['CN'] = self._china_commands.get(category, [])
                elif market == 'JP':
                    variations['JP'] = self._japan_commands.get(category, [])
                elif market == 'KR':
                    variations['KR'] = self._korea_commands.get(category, [])

        return {
            'query_id': query_id,
            'base_command': base_command,
            'category': category,
            'variations': variations,
            'markets_checked': markets or ['NA', 'DE', 'FR', 'ES', 'CN', 'JP', 'KR'],
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_market_config(self) -> Dict[str, Any]:
        """
        Get market-specific commands configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_market_config()
        """
        return {
            'supported_markets': {
                'NA': ['US', 'CA', 'MX'],
                'EU': list(self._eu_commands.keys()),
                'APAC': ['CN', 'JP', 'KR'],
                'MENA': list(self._mena_commands.keys())
            },
            'command_categories': list(self._na_commands.keys()),
            'total_na_commands': sum(len(v) for v in self._na_commands.values()),
            'total_eu_countries': len(self._eu_commands),
            'features': [
                'na_commands', 'eu_commands', 'asian_markets',
                'mena_commands', 'translation', 'variations'
            ]
        }
