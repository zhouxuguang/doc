for file in *.mp4; do
  ffmpeg -i "$file" -vf "fps=60,scale=2054:-1:flags=lanczos" -c:v gif "${file%.mp4}.gif"
done
