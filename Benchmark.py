# benchmark.py
# Medir una configuracion (tamano, procesos) a la vez y generar graficas.
#
# Uso (con el venv ACTIVADO, sin ruta explicita al python):
#   python benchmark.py --tam 500 --procesos 4
#   python benchmark.py --tam 1000 --procesos 8 --generaciones 10
#   python benchmark.py --graficar
#
# Requiere: mpi4py, matplotlib (instalados en el venv).

import argparse
import os
import subprocess
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ARCHIVO_RESULTADOS = "resultados.txt"


# ---------------------- Worker (corre con mpiexec) ----------------------
def worker(args):
    from mpi4py import MPI
    from parcial1 import crearMatriz, medirSecuencial, medirParalela

    rango = MPI.COMM_WORLD.Get_rank()
    procesos = MPI.COMM_WORLD.Get_size()

    # Solo el proceso 0 crea la matriz, igual que en parcial1
    matriz = crearMatriz(args.tam, args.tam) if rango == 0 else None

    if args.modo == "secuencial":
        if rango == 0:
            _, t = medirSecuencial(matriz, args.generaciones)
            print(f"TIEMPO {t}")
    else:
        _, t = medirParalela(matriz, args.generaciones)
        if rango == 0:
            print(f"TIEMPO {t}")


# ---------------------- Lanzar mpiexec ----------------------
def correr(python, script, procesos, tam, generaciones, modo):
    cmd = ["mpiexec", "-n", str(procesos), python, script, "--worker",
           "--modo", modo, "--tam", str(tam), "--generaciones", str(generaciones)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        raise RuntimeError("Fallo al ejecutar: " + " ".join(cmd))
    for linea in r.stdout.splitlines():
        if linea.startswith("TIEMPO "):
            return float(linea.split()[1])
    raise RuntimeError("No se obtuvo tiempo.\nSTDOUT:\n" + r.stdout + "\nSTDERR:\n" + r.stderr)


# ---------------------- Guardar (actualiza si repites) ----------------------
def guardar(tam, procs, gen, t_sec, t_par):
    datos = {}
    if os.path.exists(ARCHIVO_RESULTADOS):
        with open(ARCHIVO_RESULTADOS) as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    p = linea.split(",")
                    if len(p) == 5:
                        datos[(int(p[0]), int(p[1]))] = linea
    datos[(tam, procs)] = f"{tam},{procs},{gen},{t_sec},{t_par}"
    with open(ARCHIVO_RESULTADOS, "w") as f:
        for k in sorted(datos):
            f.write(datos[k] + "\n")


# ---------------------- Modo medir ----------------------
def medir(tam, procesos, generaciones):
    python = sys.executable          # el del venv, porque corriste con `python`
    script = os.path.abspath(__file__)

    print(f"Secuencial (1 proceso, {tam}x{tam}, {generaciones} gen)...")
    t_sec = correr(python, script, 1, tam, generaciones, "secuencial")
    print(f"  Tiempo: {t_sec:.4f} s")

    print(f"Paralelo ({procesos} procesos, {tam}x{tam}, {generaciones} gen)...")
    t_par = correr(python, script, procesos, tam, generaciones, "paralelo")
    print(f"  Tiempo: {t_par:.4f} s")

    speedup = t_sec / t_par if t_par > 0 else 0
    print(f"Speedup: {speedup:.3f}x")

    guardar(tam, procesos, generaciones, t_sec, t_par)
    print(f"Guardado en {ARCHIVO_RESULTADOS}")


# ---------------------- Modo graficar ----------------------
def graficar():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not os.path.exists(ARCHIVO_RESULTADOS):
        print(f"No existe {ARCHIVO_RESULTADOS}. Corre primero el benchmark.")
        return

    # datos[(tam, procs)] = (gen, t_sec, t_par)
    datos = {}
    with open(ARCHIVO_RESULTADOS) as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            tam, procs, gen, t_sec, t_par = linea.split(",")
            datos[(int(tam), int(procs))] = (int(gen), float(t_sec), float(t_par))

    if not datos:
        print("Sin datos.")
        return

    tamanos = sorted({k[0] for k in datos})
    procesos = sorted({k[1] for k in datos})
    generaciones = next(iter(datos.values()))[0]

    # --- Grafica 1: tiempo vs tamano ---
    plt.figure(figsize=(8, 5))
    # Secuencial: el tiempo secuencial guardado en cualquier fila de ese tamano
    t_sec_por_tam = {}
    for (tam, _), (_, ts, _) in datos.items():
        t_sec_por_tam[tam] = ts
    plt.plot(tamanos, [t_sec_por_tam[t] for t in tamanos],
             marker="o", linewidth=2, label="Secuencial")
    for p in procesos:
        xs, ys = [], []
        for tam in tamanos:
            if (tam, p) in datos:
                xs.append(tam)
                ys.append(datos[(tam, p)][2])
        if xs:
            plt.plot(xs, ys, marker="o", linewidth=2, label=f"Paralelo ({p} proc)")
    plt.xlabel("Tamano matriz (N x N)")
    plt.ylabel("Tiempo (s)")
    plt.title(f"Tiempo vs tamano ({generaciones} generaciones)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("grafica_tiempo_vs_tamano.png", dpi=150)
    print("Guardada: grafica_tiempo_vs_tamano.png")

    # --- Grafica 2: tiempo vs procesos ---
    plt.figure(figsize=(8, 5))
    for tam in tamanos:
        xs, ys = [], []
        for p in procesos:
            if (tam, p) in datos:
                xs.append(p)
                ys.append(datos[(tam, p)][2])
        if xs:
            plt.plot(xs, ys, marker="o", linewidth=2, label=f"{tam}x{tam}")
    plt.xlabel("Numero de procesos")
    plt.ylabel("Tiempo (s)")
    plt.title(f"Tiempo vs procesos ({generaciones} generaciones)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("grafica_tiempo_vs_procesos.png", dpi=150)
    print("Guardada: grafica_tiempo_vs_procesos.png")

    # --- Grafica 3: speedup ---
    plt.figure(figsize=(8, 5))
    for tam in tamanos:
        xs, ys = [], []
        for p in procesos:
            if (tam, p) in datos:
                _, ts, tp = datos[(tam, p)]
                xs.append(p)
                ys.append(ts / tp if tp > 0 else 0)
        if xs:
            plt.plot(xs, ys, marker="o", linewidth=2, label=f"{tam}x{tam}")
    plt.plot(procesos, procesos, "k--", alpha=0.4, label="Ideal (lineal)")
    plt.xlabel("Numero de procesos")
    plt.ylabel("Speedup (T_sec / T_par)")
    plt.title(f"Speedup ({generaciones} generaciones)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("grafica_speedup.png", dpi=150)
    print("Guardada: grafica_speedup.png")


# ---------------------- Punto de entrada ----------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Juego de la Vida")
    parser.add_argument("--tam", type=int, help="tamano de la matriz (NxN)")
    parser.add_argument("--procesos", type=int, help="numero de procesos para la version paralela")
    parser.add_argument("--generaciones", type=int, default=10)
    parser.add_argument("--graficar", action="store_true", help="generar graficas desde resultados.txt")

    # Internos (los usa el worker lanzado por mpiexec)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--modo", choices=["secuencial", "paralelo"], help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.worker:
        worker(args)
    elif args.graficar:
        graficar()
    else:
        if args.tam is None or args.procesos is None:
            parser.error("Debes indicar --tam y --procesos (o usar --graficar)")
        medir(args.tam, args.procesos, args.generaciones)