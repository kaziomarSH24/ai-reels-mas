<?php
$content = file_get_contents('app/Filament/Resources/GeneratedReels/GeneratedReelResource.php');

// Replace the previous custom formatStateUsing
$search = "->formatStateUsing(fn (\$state) => \"<video controls src='{\$state}' style='height: 180px; border-radius: 0.5rem; background-color: #000; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'></video>\")\n                    ->html()";
$replace = "->formatStateUsing(fn (\$state) => '▶ Play Short/Reel')
                    ->badge()
                    ->color('info')
                    ->action(
                        \\Filament\\Tables\\Actions\\Action::make('play_video')
                            ->modalHeading(fn (\$record) => 'Preview: ' . \$record->target_word)
                            ->modalSubmitAction(false)
                            ->modalCancelActionLabel('Close Player')
                            ->modalWidth('sm')
                            ->modalContent(fn (\$record) => view('filament.components.video-modal', ['url' => \$record->file_path]))
                    )";

$newContent = str_replace($search, $replace, $content);

if ($newContent === $content) {
    echo "Replace failed! Search string not found.";
} else {
    file_put_contents('app/Filament/Resources/GeneratedReels/GeneratedReelResource.php', $newContent);
    echo "Replaced successfully!";
}
