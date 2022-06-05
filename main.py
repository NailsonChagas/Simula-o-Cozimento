"""

Simulação de cozimento

Equação do Calor --> equação da difusão (térmica)

∂u/∂t =  η ( ∇²u )

u -> campo de temperaturas
t -> tempo
η -> coeficiente de difusão térmica
∇ -> Laplaciano

fonte: https://pt.wikipedia.org/wiki/Equa%C3%A7%C3%A3o_do_calor  :)

Esta simulação é bidimensional

"""

import json
import numba
from numba import jit

import numpy as np
from skimage import io
from skimage import color
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import PillowWriter

numba.jit("f8[:,:,:](f8[:,:,:], b1[:,:])", nopython=True, nogil=True)
def solve_heat(heatmap, frango, coef_frango, iteracoes, delta, dx, dt):
    cs = heatmap[0].copy() #current state
    length = len(cs[0])
    cf = 0 # current frame
    cont = 0
    for t in range(1,iteracoes):
        ns = cs.copy() # new state
        for i in range(1, length-1):
            for j in range(1, length-1):
                print(cont)
                cont += 1
                if frango[j][i]:
                    a = coef_frango
                    ns[j][i] = cs[j][i] + a*dt/dx**2 * (cs[j+1][i] + cs[j-1][i] +\
                                                    cs[j][i+1] + cs[j][i-1] -\
                                                    4*cs[j][i])
        cs = ns.copy()
        if t%delta==0:
            cf = cf + 1
            heatmap[cf] = cs
            
    return heatmap

def main():
    borda = np.linspace(0, 1, 600) #imagem 600x600
    xv, yv = np.meshgrid(borda, borda)
    imagem = color.rgb2gray(io.imread('./img/frango_red100-2.png')[:,:,:3])
    imagem = np.flip(imagem, axis=0) #imagem é armazenada invertida no computador (????)

    frango_cor_bool = imagem < 0.9 # array -> se claridade >= 1 false / se claridade < 1 true
    coef_frango = 1.45e-7 #fonte: https://docplayer.com.br/59218406-Determinacao-da-condutividade-termica-e-difusividade-termica-da-carne-de-frango.html

    frango_cru_temp = 273.15 # em Kelvin ou 0ºC
    forno_temp = 273.15 + 180 # em Kelvin ou 180ºC

    #lista criada a baixo dira qual a temperatura inicial em cada ponto do sistema forno + frango
    temp_ini = np.zeros([100, 100]) + forno_temp
    temp_ini[frango_cor_bool] = frango_cru_temp

    edo_iter = 36000 #numero de vezes q a EDO sera atualizada (iterações do programa)
    img_num = 3600 #numero de imagens do forno que serão tiradas
    delta_img = int(edo_iter/img_num) #de quantas em quantas iterações a imagem vai ser tirada
    lista_img = np.zeros([img_num, 100, 100])
    lista_img[0] = temp_ini

    x = 0.6 # 3 considerando q o frango tem 60cm
    dx = 0.6/600
    dt = 1 # 1 segundo --> (36000/1)/3600 = frango assando por 10h

    lista_img = solve_heat(lista_img, frango_cor_bool, coef_frango, edo_iter, delta_img, dx, dt)
    
    #aux = lista_img.tolist()
    #json_str = json.dumps(aux)
    #with open('json_data.json', 'w') as outfile:
    #    json.dump(json_str, outfile)

    #covertendo para ºC
    lista_img -= 273.15

    heat_map = plt.get_cmap('inferno')

    def animate(i):
        ax.clear()
        ax.contourf(lista_img[10*i], 100, cmap=heat_map, vmin=frango_cru_temp-273.15, vmax = forno_temp-273.15)

        return fig,

    fig, ax = plt.subplots(figsize=(8,6))
    ani = animation.FuncAnimation(fig, animate,
                                frames=359, interval=50)
    ani.save('cooked.gif',writer='pillow',fps=30)

    plt.figure(figsize=(8,8))
    a = plt.contourf(lista_img[-1], 100, cmap=heat_map, vmin=frango_cru_temp-273.15, vmax=forno_temp-273.15)
    plt.colorbar()
    plt.show()

if __name__ == "__main__":
    main()