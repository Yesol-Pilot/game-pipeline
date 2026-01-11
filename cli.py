#!/usr/bin/env python
"""
게임 파이프라인 CLI
명령행 인터페이스
"""

import argparse
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))


def cmd_new(args):
    """새 게임 생성"""
    from core.gdd_generator.gdd_generator import GDDGenerator
    
    print(f"🎮 새 게임 생성: {args.name}")
    print(f"  템플릿: {args.template}")
    
    generator = GDDGenerator({"provider": "gemini"})
    gdd = generator.generate_from_trends([], [], args.template)
    
    output_path = f"games/{args.name}/gdd.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generator.save_gdd(gdd, output_path)
    
    print(f"✅ GDD 저장: {output_path}")


def cmd_build(args):
    """게임 빌드"""
    from core.builder.godot_builder import GodotBuilder
    
    print(f"🔨 빌드 시작: {args.project}")
    print(f"  플랫폼: {', '.join(args.platforms)}")
    
    builder = GodotBuilder({"godot_path": args.godot})
    
    for platform in args.platforms:
        result = builder.build(args.project, platform, f"builds/{platform}")
        status = "✅" if result.get("success") else "❌"
        print(f"  {status} {platform}")


def cmd_deploy(args):
    """게임 배포"""
    from core.deployer.store_uploader import AppStoreUploadManager
    
    print(f"🚀 배포: {args.build}")
    print(f"  스토어: {args.store}")
    
    manager = AppStoreUploadManager({})
    # 실제 배포 로직
    print("✅ 배포 완료 (시뮬레이션)")


def cmd_serve(args):
    """웹 대시보드 실행"""
    from core.web.dashboard_server import run_server
    
    print(f"🌐 대시보드 시작: http://{args.host}:{args.port}")
    run_server(args.host, args.port)


def cmd_test(args):
    """테스트 실행"""
    import subprocess
    
    print("🧪 테스트 실행...")
    
    cmd = ["pytest", "-v"]
    if args.coverage:
        cmd.extend(["--cov=core", "--cov-report=html"])
    
    subprocess.run(cmd)


def cmd_lint(args):
    """린트 실행"""
    import subprocess
    
    print("🔍 코드 검사...")
    
    if args.fix:
        print("  포맷팅 (black)...")
        subprocess.run(["black", "core/"])
        
        print("  정렬 (isort)...")
        subprocess.run(["isort", "core/"])
    else:
        print("  린트 (pylint)...")
        subprocess.run(["pylint", "core/", "--disable=C,R"])


def main():
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="🎮 초자동화 게임 개발 파이프라인 CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="명령어")
    
    # new 명령어
    new_parser = subparsers.add_parser("new", help="새 게임 생성")
    new_parser.add_argument("name", help="게임 이름")
    new_parser.add_argument("-t", "--template", default="runner",
                           choices=["runner", "puzzle", "clicker", "match3", "rhythm", "idle"],
                           help="템플릿 유형")
    new_parser.set_defaults(func=cmd_new)
    
    # build 명령어
    build_parser = subparsers.add_parser("build", help="게임 빌드")
    build_parser.add_argument("project", help="프로젝트 경로")
    build_parser.add_argument("-p", "--platforms", nargs="+", 
                             default=["html5"],
                             help="빌드 플랫폼")
    build_parser.add_argument("--godot", default="godot", help="Godot 경로")
    build_parser.set_defaults(func=cmd_build)
    
    # deploy 명령어
    deploy_parser = subparsers.add_parser("deploy", help="게임 배포")
    deploy_parser.add_argument("build", help="빌드 파일 경로")
    deploy_parser.add_argument("-s", "--store", default="google_play",
                              choices=["google_play", "app_store", "steam"],
                              help="스토어")
    deploy_parser.set_defaults(func=cmd_deploy)
    
    # serve 명령어
    serve_parser = subparsers.add_parser("serve", help="웹 대시보드 실행")
    serve_parser.add_argument("--host", default="0.0.0.0", help="호스트")
    serve_parser.add_argument("--port", type=int, default=8000, help="포트")
    serve_parser.set_defaults(func=cmd_serve)
    
    # test 명령어
    test_parser = subparsers.add_parser("test", help="테스트 실행")
    test_parser.add_argument("--coverage", action="store_true", help="커버리지 포함")
    test_parser.set_defaults(func=cmd_test)
    
    # lint 명령어
    lint_parser = subparsers.add_parser("lint", help="코드 검사")
    lint_parser.add_argument("--fix", action="store_true", help="자동 수정")
    lint_parser.set_defaults(func=cmd_lint)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
