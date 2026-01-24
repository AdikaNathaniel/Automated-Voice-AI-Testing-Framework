#!/usr/bin/env python3
"""
Script to replace all emoji icons with Lucide icon equivalents
"""
import re

# Mapping of emojis to Lucide icon names
EMOJI_TO_LUCIDE = {
    # Navigation
    '📊': 'layout-dashboard',
    '🧪': 'flask-conical',
    '📈': 'trending-up',
    '✓': 'check-circle',
    '📄': 'file-text',

    # Actions
    '⚠️': 'alert-triangle',
    '🔔': 'bell',
    '⚙️': 'settings',
    '🔍': 'search',
    '🔄': 'rotate-cw',
    '💰': 'dollar-sign',
    '👁': 'eye',
    '👁️': 'eye',
    '⏳': 'clock',
    '📋': 'clipboard-list',
    '⚡': 'zap',
    '❌': 'x-circle',
    '✗': 'x',
    '✕': 'x',
    '📜': 'scroll',
    '💡': 'lightbulb',
    '🎯': 'target',
    '🔥': 'flame',
    '⏸': 'pause',
    '⏹': 'square',
    '⏭': 'skip-forward',
    '🚀': 'rocket',
    '✨': 'sparkles',
    '▶': 'play',
    '▶️': 'play',
    '🎵': 'audio-lines',
    '📝': 'file-edit',
    '🔗': 'link',
    '💯': 'percent',
    '🎨': 'palette',
    '📑': 'file-stack',
    '📚': 'history',
    '⏰': 'calendar-clock',
    '📥': 'download',
    '👥': 'users',
    '🤖': 'brain',
    '⭐': 'star',
    '☆': 'star',
    '🔬': 'microscope',
    '🔐': 'lock',
    '🌐': 'globe',
    '📱': 'smartphone',
    '💼': 'briefcase',
    '🏆': 'trophy',
    '📞': 'phone',
    '🌡️': 'thermometer',
    '🎤': 'mic',
    '🎧': 'headphones',
    '📡': 'radio',
    '🖥️': 'monitor',
    '💻': 'laptop',
    '📲': 'smartphone',
    '🔋': 'battery',
    '✏️': 'edit',
    '🗑️': 'trash-2',
    '💾': 'save',
    '↩️': 'corner-down-left',
    'ℹ️': 'info',
    '🌍': 'globe',
}

def replace_emoji_in_line(line):
    """Replace emojis in a line with Lucide icon components"""
    result = line

    for emoji, icon_name in EMOJI_TO_LUCIDE.items():
        if emoji in result:
            # Different replacement strategies based on context

            # For icon data properties
            if f"icon: '{emoji}'" in result:
                result = result.replace(f"icon: '{emoji}'", f"icon: '{icon_name}'")

            # For inline text (with margin)
            elif f"{emoji} " in result or f" {emoji}" in result:
                # Determine icon size based on context
                if 'className="metric-icon"' in result or 'template-icon' in result:
                    size = '20px'
                elif 'font-size: 48px' in result or 'empty-icon' in result or 'fontSize: \'48px\'' in result:
                    size = '48px'
                elif 'font-size: 64px' in result or 'fontSize: \'64px\'' in result:
                    size = '64px'
                elif 'fontSize: \'20px\'' in result or 'className="section-icon"' in result:
                    size = '20px'
                else:
                    size = '14px'

                icon_html = f'<i data-lucide="{icon_name}" style={{{{width: \'{size}\', height: \'{size}\'}}}}></i>'

                # Replace with spacing considerations
                result = result.replace(f'{emoji} ', f'{icon_html} ')
                result = result.replace(f' {emoji}', f' {icon_html}')
                result = result.replace(f'>{emoji}<', f'>{icon_html}<')

    return result

# Process test-management.html
input_file = '/home/ubuntu/workspace/automated-testing/test-management.html'
output_file = '/home/ubuntu/workspace/automated-testing/test-management_fixed.html'

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for line in lines:
    output_lines.append(replace_emoji_in_line(line))

with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"Processed {input_file}")
print(f"Output written to {output_file}")
print("Review the file and rename if correct.")
