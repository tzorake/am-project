import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif',
})

ax=plt.subplot(111)
ax.text(0.5,0.5,r'$\frac{a}{b}$',fontsize=30,color="green")
ax.set_xlabel(r'$\omega$', fontsize=18)
ax.set_ylabel(r'$x$', fontsize=18)
plt.show()