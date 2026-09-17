import re

with open("app/Filament/Pages/ContentStrategy.php", "r") as f:
    content = f.read()

old_prompt = """            $prompt = "You are an expert Social Media Strategist and English Teacher for a Bengali audience on TikTok/YouTube Shorts. " .
                      "Here is a list of English vocabulary words available in my database right now: [ $wordsList ]. " .
                      "Please analyze these words and recommend the TOP 5 best words for me to make video reels on TODAY. " .
                      "Pick words that are trendy, emotionally impactful, or highly useful in daily conversation. " .
                      "For each word, provide: 1) The Word, 2) The Bengali Meaning, 3) Why it makes a great viral video reel. " .
                      "Format your response in beautiful Markdown, using bold text, bullet points, and emojis. Respond in Bengali.";"""

new_prompt = """            $prompt = "You are an expert Social Media Strategist and English Teacher for a Bengali audience on TikTok/YouTube Shorts. " .
                      "Here is the STRICT list of English vocabulary words available in my database right now: [ $wordsList ]. " .
                      "Please analyze ONLY these provided words and recommend up to 5 of the best words for me to make video reels on TODAY. " .
                      "CRITICAL RULE: You MUST ONLY select words that are exactly present in the list above. DO NOT invent, suggest, or add any outside words. If there are fewer than 5 words in the list, just review whatever is available. " .
                      "Pick words that are trendy, emotionally impactful, or highly useful in daily conversation. " .
                      "For each chosen word, provide: 1) The Word, 2) The Bengali Meaning, 3) Why it makes a great viral video reel. " .
                      "Format your response in beautiful Markdown, using bold text, bullet points, and emojis. Respond in Bengali.";"""

content = content.replace(old_prompt, new_prompt)

with open("app/Filament/Pages/ContentStrategy.php", "w") as f:
    f.write(content)
