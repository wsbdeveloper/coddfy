"""
Popula o banco com todas as massas de exemplo.

Ordem:
  1. seed_partners.py  — parceiros e usuários de parceiro
  2. seed_data.py      — clientes, contratos, consultores, parcelas base
  3. seed_installments.py — parcelas extras (opcional)

Uso local:
  poetry run python backend/scripts/seed_all.py

Docker:
  docker exec ccm_backend sh -c "cd backend && python scripts/seed_all.py"
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_script(script_name: str) -> None:
    scripts_dir = Path(__file__).resolve().parent
    script_path = scripts_dir / script_name
    print(f"\n>>> Executando {script_name}\n")
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Popula o banco com massas de exemplo")
    parser.add_argument(
        "--with-extra-installments",
        action="store_true",
        help="Cria parcelas adicionais para todos os contratos (pode duplicar se já existirem)",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("🌱 Seed completo — Coddfy CCM")
    print("=" * 80)

    run_script("seed_partners.py")
    run_script("seed_data.py")

    if args.with_extra_installments:
        run_script("seed_installments.py")

    print()
    print("=" * 80)
    print("✅ Massas criadas com sucesso!")
    print("=" * 80)
    print()
    print("Logins disponíveis:")
    print("  admin / admin123          (admin global)")
    print("  admin_robbin / robbin123  (admin parceiro Robbin)")
    print("  user_robbin / robbin123   (usuário parceiro Robbin)")
    print()


if __name__ == "__main__":
    main()
