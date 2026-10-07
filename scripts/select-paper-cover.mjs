#!/usr/bin/env node
import { createHash, randomInt } from 'node:crypto'
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { parseArgs } from 'node:util'
import { parseFrontmatter } from '@astrojs/markdown-remark'

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const catalogUrl = 'https://pic.agusexp25.top/covers/library/catalog.json'
const help = `用法：
  pnpm covers:select -- --post src/content/blog/paper-deep-dive-<slug>/index.mdx --write

选项：
  --category <类别>   按类别筛选，如 芙莉莲、动漫风景、边缘行者
  --id <图片编号>     使用目录中的指定图片
  --replace          更换已有封面（默认保留）
  --write            写入文章；省略时仅输出 JSON
  --blog-root <目录>  博客根目录，默认此脚本所在仓库
  --catalog <地址>    图片目录 URL 或本地 JSON，默认个人图床目录
  --help             显示帮助
`

const hash = (text) => createHash('sha256').update(text.replace(/\r\n/g, '\n')).digest('hex')

function readPost(filename) {
  const text = readFileSync(filename, 'utf8')
  return { filename, text, ...parseFrontmatter(text) }
}

function listPosts(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const filename = path.join(directory, entry.name)
    if (entry.isDirectory()) return listPosts(filename)
    return /^index(?:-en)?\.mdx?$/.test(entry.name) ? [readPost(filename)] : []
  })
}

function coverFields(frontmatter) {
  if (!frontmatter.heroImage?.src) return {}
  return {
    heroImage: frontmatter.heroImage,
    ...(frontmatter.pixivLink ? { pixivLink: String(frontmatter.pixivLink) } : {})
  }
}

function matchUrl(url) {
  return typeof url === 'string' ? url.split(/[?#]/)[0] : ''
}

function entryUrls(entry) {
  return [entry.url, entry.originalUrl].filter(Boolean).map(matchUrl)
}

function updatePost(post, fields, blogRoot) {
  // Change only cover fields; keep the rest of the frontmatter and MDX verbatim.
  const envelope = /^(\uFEFF?---\r?\n)([\s\S]*?)(\r?\n---(?:\r?\n|$))/.exec(post.text)
  if (!envelope) throw new Error('文章需要 YAML frontmatter：' + post.filename)
  const newline = post.text.includes('\r\n') ? '\r\n' : '\n'
  const lines = envelope[2].split(/\r?\n/)
  const remaining = []
  let skipping = false
  for (const line of lines) {
    if (/^(?:heroImage|pixivLink|"heroImage"|"pixivLink"|'heroImage'|'pixivLink')\s*:/.test(line)) {
      skipping = true
    } else if (skipping && (line.trim() === '' || /^\s/.test(line))) {
      continue
    } else {
      skipping = false
      remaining.push(line)
    }
  }
  const additions = Object.entries(fields).map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
  const next =
    envelope[1] +
    [...remaining, ...additions].join(newline) +
    envelope[3] +
    post.text.slice(envelope[0].length)
  const parsed = parseFrontmatter(next).frontmatter
  if (JSON.stringify(coverFields(parsed)) !== JSON.stringify(fields)) {
    throw new Error('封面字段写入校验失败')
  }
  const manifestPath = path.join(path.dirname(post.filename), 'export-manifest.json')
  let manifest
  if (existsSync(manifestPath)) {
    manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
    const relative = path.relative(blogRoot, post.filename).split(path.sep).join('/')
    if (manifest.files?.[relative] !== hash(post.text)) {
      throw new Error('导入文章存在其他修改，请先合并正文修改后再更新封面：' + relative)
    }
    manifest.files[relative] = hash(next)
    manifest.heroImage = fields.heroImage
    if (fields.pixivLink) manifest.pixivLink = fields.pixivLink
    else delete manifest.pixivLink
  }
  writeFileSync(post.filename, next)
  if (manifest) writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n')
}

async function main() {
  const { values } = parseArgs({
    args: process.argv.slice(2).filter((arg) => arg !== '--'),
    options: {
      post: { type: 'string' },
      category: { type: 'string' },
      id: { type: 'string' },
      replace: { type: 'boolean' },
      write: { type: 'boolean' },
      'blog-root': { type: 'string', default: projectRoot },
      catalog: { type: 'string', default: catalogUrl },
      help: { type: 'boolean' }
    }
  })
  if (values.help) return console.log(help)
  if (!values.post) throw new Error('请指定 --post <文章路径>')
  const blogRoot = path.resolve(values['blog-root'])
  const contentRoot = path.join(blogRoot, 'src/content/blog')
  const filename = path.resolve(blogRoot, values.post)
  const relative = path.relative(contentRoot, filename)
  if (
    relative.startsWith('..') ||
    path.isAbsolute(relative) ||
    !/^index(?:-en)?\.mdx?$/.test(path.basename(filename))
  ) {
    throw new Error('--post 必须是 src/content/blog 中的 index.md(x) 或 index-en.md(x)')
  }
  const post = existsSync(filename) ? readPost(filename) : undefined
  if (values.write && !post) throw new Error('请先创建文章，再使用 --write')
  const existing = coverFields(post?.frontmatter ?? {})
  if (existing.heroImage && !values.replace) {
    console.log(JSON.stringify({ action: 'kept', frontmatter: existing }, null, 2))
    return
  }

  let catalog
  try {
    if (/^https?:\/\//.test(values.catalog)) {
      const response = await fetch(values.catalog, { signal: AbortSignal.timeout(20000) })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      catalog = await response.json()
    } else {
      catalog = JSON.parse(readFileSync(path.resolve(blogRoot, values.catalog), 'utf8'))
    }
  } catch (error) {
    process.exitCode = 2
    throw new Error('无法读取封面目录：' + error.message)
  }
  const entries = catalog.entries
  if (!Array.isArray(entries) || !entries.length) throw new Error('封面目录为空')
  const aliases = {
    动漫风景: '风景',
    二次元人物: '人物',
    fulilian: '芙莉莲',
    frieren: '芙莉莲',
    edgerunners: '边缘行者'
  }
  const category = aliases[values.category?.toLowerCase()] ?? values.category
  let candidates = entries.filter(
    (entry) =>
      (!category ||
        entry.groups?.some((group) => group.toLowerCase().includes(category.toLowerCase()))) &&
      (!values.id || entry.id === values.id || entry.canonicalId === values.id)
  )
  if (!candidates.length) throw new Error('没有匹配的封面，请检查类别或图片编号')
  if (values.replace && existing.heroImage && !values.id) {
    candidates = candidates.filter(
      (entry) => !entryUrls(entry).includes(matchUrl(existing.heroImage.src))
    )
  }
  if (!candidates.length) throw new Error('该类别没有其他可替换的封面')
  const posts = listPosts(contentRoot)
  // Count one article once even when its Chinese and English versions share a cover.
  const usage = (entry) => [
    ...new Set(
      posts
        .filter(
          (item) =>
            entryUrls(entry).includes(matchUrl(item.frontmatter.heroImage?.src)) ||
            (entry.pixivId && String(item.frontmatter.pixivLink) === String(entry.pixivId))
        )
        .map((item) =>
          path.relative(contentRoot, path.dirname(item.filename)).split(path.sep).join('/')
        )
    )
  ]
  const ranked = candidates.map((entry) => ({ entry, usedIn: usage(entry) }))
  const minimum = Math.min(...ranked.map((item) => item.usedIn.length))
  const pool = ranked.filter((item) => item.usedIn.length === minimum)
  const { entry, usedIn } = pool[randomInt(pool.length)]
  const frontmatter = {
    heroImage: {
      src: entry.url,
      alt: (entry.groups ?? []).join(' · ') + '插画封面',
      width: entry.width,
      height: entry.height
    },
    ...(entry.pixivId ? { pixivLink: String(entry.pixivId) } : {})
  }
  if (values.write) updatePost(post, frontmatter, blogRoot)
  console.log(
    JSON.stringify(
      {
        action: values.write ? 'written' : 'selected',
        id: entry.id,
        groups: entry.groups,
        source: entry.source ?? entry.discoveryPage,
        usageCount: usedIn.length,
        usedIn,
        frontmatter
      },
      null,
      2
    )
  )
}

main().catch((error) => {
  console.error(error.message)
  process.exitCode ||= 1
})
