/* Build-only: run with Sharp available on NODE_PATH. No runtime dependency. */
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');

const assets = path.resolve(__dirname, '../adapters/openai/assets');
const source = fs.readFileSync(path.join(assets, 'sparklaunch.svg'), 'utf8');
// The canonical SVG places its background first, then rocket/rays, then the
// outlined wordmark. Keep native paths and clipping, without text or background.
const wordmarkStart = source.indexOf('<g fill="#334155"');
if (wordmarkStart < 0 || !source.includes('<defs>')) {
  throw new Error('Canonical SVG layout changed; inspect the mark before rebuilding.');
}
const mark = source.slice(0, wordmarkStart).replace(/<rect\b[^>]*\/>/g, '') + '</svg>';
const variants = [
  { name: 'sparklaunch-directory-dark.png', size: 1024, inset: 108, color: '#F1F5F9' },
  { name: 'sparklaunch-composer-48.png', size: 48, inset: 3, color: '#334155' },
];

async function build() {
  for (const variant of variants) {
    const svg = mark.replaceAll('#334155', variant.color);
    const rendered = await sharp(Buffer.from(svg), { density: 192 }).png().toBuffer();
    const trimmed = await sharp(rendered).trim().png().toBuffer();
    const inner = variant.size - 2 * variant.inset;
    const { data, info } = await sharp(trimmed)
      .resize(inner, inner, { fit: 'contain', background: '#00000000' })
      .extend({
        top: variant.inset, bottom: variant.inset,
        left: variant.inset, right: variant.inset,
        background: '#00000000',
      })
      .ensureAlpha().raw().toBuffer({ resolveWithObject: true });
    // Resampling preserves alpha but can round RGB at translucent edges.
    // Keep the owner's exact flat brand color at every alpha level.
    const rgb = variant.color.match(/[a-f\d]{2}/gi).map(value => parseInt(value, 16));
    for (let offset = 0; offset < data.length; offset += 4) {
      data[offset] = rgb[0];
      data[offset + 1] = rgb[1];
      data[offset + 2] = rgb[2];
    }
    const output = path.join(assets, variant.name);
    // RGB was explicitly replaced above, so it is no longer premultiplied.
    const raw = { width: info.width, height: info.height, channels: 4 };
    await sharp(data, { raw }).png().toFile(output);
    const verified = await sharp(output).raw().toBuffer();
    let visiblePixels = 0;
    for (let offset = 0; offset < verified.length; offset += 4) {
      if (verified[offset + 3] > 0) visiblePixels++;
      if (verified[offset] !== rgb[0] || verified[offset + 1] !== rgb[1] || verified[offset + 2] !== rgb[2]) {
        throw new Error(`${variant.name}: encoded PNG changed the exact brand color`);
      }
    }
    const last = variant.size - 1;
    const corners = [0, last, last * variant.size, variant.size ** 2 - 1];
    const transparentCorners = corners.every(pixel => verified[pixel * 4 + 3] === 0);
    if (info.width !== variant.size || info.height !== variant.size || !transparentCorners || visiblePixels === 0) {
      throw new Error(`${variant.name}: invalid size or missing transparency`);
    }
    console.log(`${variant.name}: ${variant.size}x${variant.size}, ${variant.color}, transparent`);
  }
}

build().catch(error => { console.error(error.message); process.exitCode = 1; });
