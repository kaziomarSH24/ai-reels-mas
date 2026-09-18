<?php
$content = file_get_contents('app/Filament/Resources/GeneratedReels/GeneratedReelResource.php');
$search = "->formatStateUsing(fn (\$state) => \"<a href='{\$state}' target='_blank' class='text-primary-600 underline'>Watch Video</a>\")";
$replace = "->formatStateUsing(fn (\$state) => \"<video controls src='{\$state}' style='height: 180px; border-radius: 0.5rem; background-color: #000; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'></video>\")";
$newContent = str_replace($search, $replace, $content);
file_put_contents('app/Filament/Resources/GeneratedReels/GeneratedReelResource.php', $newContent);
echo "Replaced successfully!";
