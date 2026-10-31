from PIL import Image
import os

docs = "/Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System/docs"
gh_path = os.path.join(docs, "screenshot_github_web_commits.png")
term_path = os.path.join(docs, "screenshot_terminal_git_log.png")
out_path = os.path.join(docs, "screenshot_git_commit_graph.png")

gh_im = Image.open(gh_path).convert("RGBA")
term_im = Image.open(term_path).convert("RGBA")

# gh_crop: top repo header + commits list
gh_crop = gh_im.crop((0, 0, 1280, 420))

# Resize to width 1650
target_w = 1650
gh_h = int(gh_crop.height * (target_w / gh_crop.width))
gh_resized = gh_crop.resize((target_w, gh_h), Image.Resampling.LANCZOS)

# term_crop: keep macOS window bar and top 12 git log lines (y=0 to 460)
term_crop = term_im.crop((0, 0, 1650, 460))
term_h = term_crop.height

# Combined
gap = 14
total_h = gh_h + term_h + gap
combined = Image.new("RGBA", (target_w, total_h), (255, 255, 255, 255))
combined.paste(gh_resized, (0, 0))
combined.paste(term_crop, (0, gh_h + gap))

combined.convert("RGB").save(out_path, quality=95)
print(f"Refined Combined Git screenshot: {out_path} ({combined.size[0]}x{combined.size[1]}, ratio={combined.size[0]/combined.size[1]:.2f})")
