source venv/bin/activate

cd vietTTS
bash ./scripts/quick_start.sh
cd ..
python get_MC.py
deactivate

cd Wav2Lip
source venv/bin/activate
python inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face "input/video.mp4" --audio "input/audio.wav" --outfile "output/result.mp4"
deactivate
cd ..
