import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider

class LSBanalyser:
    def __init__(self, img1_path, img2_path):
        self.settings = {
            'view_mode': 'RGB',
            'lsb_bit': 0,
            'figsize': (10, 5),
            'radio_pos': [0.05, 0.6, 0.2, 0.25],
            'slider_pos': [0.05, 0.5, 0.2, 0.03]
        }
        
        #self.radio = None
        #self.slider = None
        
        self.img1 = cv2.imread(img1_path)
        self.img2 = cv2.imread(img2_path)
        
        if self.img1 is None or self.img2 is None:
            raise ValueError("Could not load one or both images")

    def get_lsb_plane(self, image, bit): # Extracts specific LSB plane
        return ((image >> bit) & 1) * 255

    def convert_image(self, image, mode):
        if mode == 'RGB':
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif mode == 'Grayscale':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        elif mode == 'LSB':
            lsb = self.get_lsb_plane(image, self.settings['lsb_bit'])
            if len(lsb.shape) == 2:
                return cv2.cvtColor(lsb.astype(np.uint8), cv2.COLOR_GRAY2RGB)
            return lsb.astype(np.uint8)
        return image

    def update_display(self, event=None):
        self.ax1.clear()
        self.ax2.clear()

        for ax, img in zip([self.ax1, self.ax2], [self.img1, self.img2]):
            ax.imshow(self.convert_image(img, self.settings['view_mode']))
            ax.set_title(self.settings['view_mode'])
            ax.axis('off')

        self.fig.canvas.draw_idle()

    def mode_changed(self, label):
        self.settings['view_mode'] = label
        self.update_display()

    def bit_changed(self, val):
        self.settings['lsb_bit'] = int(val)
        self.update_display()

    def show(self):
        """Display the interactive analysis window"""
        plt.switch_backend('Qt5Agg')  # Use Qt5 backend - not tkinter
        

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=self.settings['figsize'])
        plt.subplots_adjust(left=0.3)
        
        rax = plt.axes(self.settings['radio_pos']) # Creating radio buttons
        self.radio = RadioButtons(rax, ('RGB', 'Grayscale', 'LSB'))
        self.radio.on_clicked(self.mode_changed)
        
        sax = plt.axes(self.settings['slider_pos']) # And the slider
        self.slider = Slider(sax, 'LSB Plane', 0, 7, valinit=self.settings['lsb_bit'], valstep=1)
        self.slider.on_changed(self.bit_changed)
        
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        self.update_display()
        plt.show(block=True) 

    def on_close(self, event):
        if self.radio:
            self.radio.disconnect_events()
        if self.slider:
            self.slider.disconnect_events()


def analyse_image_lsb(img1_path, img2_path): # Clean-up function

    plt.close('all')
    analyser = LSBanalyser(img1_path, img2_path)
    analyser.show()


# if __name__ == "__main__":
#     # Example usage when run directly
#     analyse_image_lsb(
#         r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\BenPNG.png",
#         r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\NoiseBen.png"
#     )