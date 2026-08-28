#!/usr/bin/env node

// 一键部署博客：本地构建 GitHub Pages 静态产物，然后提交并推送当前修改到 main。
// GitHub Actions 会在 main 推送后负责正式发布，避免本地直接维护 gh-pages 分支。
//
// 用法：
//   pnpm deploy
//   pnpm deploy:check
//   pnpm run deploy -- --message "blog: update about page"
//
// 说明：
// - 脚本不会读取或写入 .env，也不会把 token 拼进 Git remote。
// - 推送使用本机 Git 已配置的凭据（例如 Git Credential Manager）。
// - 默认只允许从 main 发布；可用 DEPLOY_BRANCH / DEPLOY_REMOTE 覆盖。

import { execFileSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const remote = process.env.DEPLOY_REMOTE || 'origin'
const branch = process.env.DEPLOY_BRANCH || 'main'
const dryRun = process.argv.includes('--dry-run')

const getOption = (name, fallback) => {
  const index = process.argv.indexOf(name)
  if (index === -1) return fallback

  const value = process.argv[index + 1]
  if (!value || value.startsWith('-')) {
    throw new Error(`${name} 需要一个参数`)
  }
  return value
}

const commitMessage = getOption(
  '--message',
  process.env.DEPLOY_COMMIT_MESSAGE || 'deploy: update site'
)

const knownOptions = new Set(['--dry-run', '--message'])
for (let index = 2; index < process.argv.length; index += 1) {
  const argument = process.argv[index]
  if (knownOptions.has(argument)) {
    if (argument === '--message') index += 1
    continue
  }
  throw new Error(`未知选项：${argument}（使用 --dry-run 或 --message <说明>）`)
}

const run = (command, args, options = {}) =>
  execFileSync(command, args, { cwd: projectRoot, stdio: 'inherit', ...options })

const runGit = (args, options = {}) => run('git', args, options)

const readGit = (args, cwd = projectRoot) =>
  execFileSync('git', args, { cwd, encoding: 'utf8' }).trim()

const runAstro = (args) => {
  // Windows 下直接调用本地 Astro CLI，避免通过 pnpm.cmd 触发 spawnSync EINVAL。
  const astroBin = path.join(projectRoot, 'node_modules', 'astro', 'astro.js')
  if (!existsSync(astroBin)) {
    throw new Error(
      '找不到本地 Astro CLI。请先运行 pnpm install --frozen-lockfile --config.confirmModulesPurge=false'
    )
  }
  run(process.execPath, [astroBin, ...args], {
    env: { ...process.env, DEPLOYMENT_PLATFORM: 'github' }
  })
}

const assertProjectRepository = () => {
  const repositoryRoot = path.resolve(readGit(['rev-parse', '--show-toplevel']))
  if (repositoryRoot.toLowerCase() !== projectRoot.toLowerCase()) {
    throw new Error(`Git 根目录不是项目目录：${repositoryRoot}`)
  }

  const currentBranch = readGit(['branch', '--show-current'])
  if (currentBranch !== branch) {
    throw new Error(
      `当前分支是 ${currentBranch || '(detached HEAD)'}，脚本默认只从 ${branch} 发布。` +
        `请先切换到 ${branch}，或设置 DEPLOY_BRANCH 指定目标分支。`
    )
  }

  readGit(['remote', 'get-url', remote])
}

const assertSafeStagedFiles = () => {
  const stagedFiles = execFileSync('git', ['diff', '--cached', '--name-only', '-z'], {
    cwd: projectRoot,
    encoding: 'utf8'
  })
    .split('\0')
    .filter(Boolean)

  const protectedFiles = stagedFiles.filter((file) =>
    /(^|[\\/])\.env(?:\..*)?$|\.(?:pem|key|p12)$|(^|[\\/])credentials(?:\..*)$/i.test(
      file
    )
  )

  if (protectedFiles.length) {
    throw new Error(
      `检测到可能包含凭据的文件，已停止提交：${protectedFiles.join(', ')}`
    )
  }
}

const main = () => {
  assertProjectRepository()

  console.log('== 步骤 1/3：以 GitHub Pages 模式构建并校验 ==')
  runAstro(['check'])
  runAstro(['build'])

  const indexFile = path.join(projectRoot, 'dist', 'index.html')
  const cnameFile = path.join(projectRoot, 'dist', 'CNAME')
  const pagefindFile = path.join(projectRoot, 'dist', 'pagefind', 'pagefind.js')
  if (!existsSync(indexFile)) {
    throw new Error('构建产物缺少 dist/index.html，构建可能失败')
  }
  if (!existsSync(cnameFile)) {
    throw new Error('构建产物缺少 dist/CNAME，请检查 public/CNAME')
  }
  if (!existsSync(pagefindFile)) {
    throw new Error('构建产物缺少 Pagefind 搜索索引：dist/pagefind/pagefind.js')
  }

  if (dryRun) {
    console.log('\n✅ dry-run 完成：已构建并校验 dist，未提交、未推送。')
    console.log('   如需本地预览：pnpm preview')
    return
  }

  console.log('\n== 步骤 2/3：提交本地修改 ==')
  const statusBeforeCommit = readGit(['status', '--porcelain'])
  if (statusBeforeCommit) {
    runGit(['add', '-A'])
    assertSafeStagedFiles()
    runGit(['commit', '-m', commitMessage])
  } else {
    console.log('没有新的文件修改，跳过 commit。')
  }

  console.log(`\n== 步骤 3/3：推送 ${remote}/${branch} ==`)
  runGit(['push', remote, branch])

  console.log('\n✅ 已推送。GitHub Actions 将自动构建并发布网站：')
  console.log('   https://github.com/Agus76677/agusexp25-blog/actions')
  console.log('   https://agusexp25.top')
}

try {
  main()
} catch (error) {
  console.error(`\n❌ 部署失败：${error.message}`)
  process.exitCode = 1
}
