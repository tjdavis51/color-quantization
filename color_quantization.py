from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import math

K = 10
IMAGE_FILE = "test1.jpeg"

########################
### helper functions ###
########################

def load_image(file_path):
    img = Image.open(file_path)
    img = img.convert("RGB")
    height = img.size[1]
    width = img.size[0]
    pixels = np.array(img).astype(float)
    pixels = pixels.reshape(-1, 3)
    return pixels, height, width

def color_quantization(pixels, centroids, cluster_list):
    for centroid_index in range(len(centroids)):
        for pixel_index in range(pixels.shape[0]):
            if cluster_list[pixel_index] == centroid_index:
                pixels[pixel_index] = centroids[centroid_index]

    return pixels

def average_pixels(pixels, color):
    sum = 0.0
    for pixel in pixels:
        current_r = pixel[color]
        sum += current_r

    return sum / len(pixels)

def eu_distance(cent, pixel):
    dist = math.sqrt(((cent[0] - pixel[0]) ** 2) + ((cent[1] - pixel[1]) ** 2) + ((cent[2] - pixel[2]) ** 2))
    return dist

def has_diff_clusters(pixels, cluster_list, previous_cluster_list):
    count = 0
    for pixel_index in range(pixels.shape[0]):
        if (cluster_list[pixel_index] == None) and (previous_cluster_list[pixel_index] == None):
            continue
        elif cluster_list[pixel_index] == previous_cluster_list[pixel_index]:
            count += 1

    if count == pixels.shape[0]:
        return False
    else:
        return True

def print_pixel(pixel):
    print(f"({pixel[0]}, {pixel[1]}, {pixel[2]})")

def print_x_pixels(pixels, x):
    # slice at x
    sliced_pixels = pixels[:x]
    pixel_strings = []
    for pixel in sliced_pixels:
        pixel_strings.append(str(pixel))
    output = ", ".join(pixel_strings)
    print(output)

# takes in a list of points and returns a list of centroids
# also assigns each point to its corresponding cluster
def k_means(pixels):

    ##############################
    ### pick initial centroids ###
    ##############################

    centroids = []
    picked = set()

    # generate unique random values
    while (len(picked) < K):
            chosen_centroid_index = random.randint(0, pixels.shape[0] - 1)
            picked.add(chosen_centroid_index)

    for index in picked:
        # access rgb values
        centroid_value_r = pixels[index][0]
        centroid_value_g = pixels[index][1]
        centroid_value_b = pixels[index][2]
        created_centroid = [centroid_value_r, centroid_value_g, centroid_value_b]
        centroids.append(created_centroid)

    # for cent in centroids:
    #     print(cent)
    # print()

    ###################################################
    ### loop while the centroids are still changing ###
    ###################################################

    # condition: if new centroids are the same as last centroids -> end
    iter_count = 0

    # save a None for each pixel's cluster
    cluster_list = []
    previous_cluster_list = []
    for _ in range(pixels.shape[0]):
        cluster_list.append(None)
        previous_cluster_list.append(None)

    while (has_diff_clusters(pixels, cluster_list, previous_cluster_list)):

        for pixel_index in range(pixels.shape[0]):
            previous_cluster_list[pixel_index] = cluster_list[pixel_index]

        ###########################
        ### make distance lists ###
        ###########################

        centroid_distances = []
        clusters = []

        for _ in range(K):
            # populate with distance lists (1 list per number of centroids)
            centroid_distances.append([])
            # populate the cluster lists (1 list per number of centroids)
            clusters.append([])

        ######################
        ### get distances ####
        ######################

        # for each centroid find the distance for each point to that centroid
        for centroid_index in range(K):
            # find the distance from the current point from each centroid
            for pixel_index in range(pixels.shape[0]):
                # pass the 3 points in
                current_dist = eu_distance(centroids[centroid_index], pixels[pixel_index])

                # fill in the correct distance for that centroid
                centroid_distances[centroid_index].append(current_dist)

        #############################################
        ### cluster the points based on distances ###
        #############################################

        # run the loop for each point to determine its cluster
        for current_pixel_index in range(pixels.shape[0]):
            min_value = math.inf
            min_index = None
            # loop through the centroid lists to get a single list
            for current_centroid_list_index in range(K):
                if centroid_distances[current_centroid_list_index][current_pixel_index] < min_value:
                    min_value = centroid_distances[current_centroid_list_index][current_pixel_index]
                    min_index = current_centroid_list_index

            # convert to new data structure
            # point_list[current_point_index].cluster = min_index
            cluster_list[current_pixel_index] = min_index


        ############################
        ### update the centroids ###
        ############################

        # save a list of points for that cluster
        for cluster_index in range(K):
            for pixel_index in range(pixels.shape[0]):
                if cluster_list[pixel_index] == cluster_index:
                    clusters[cluster_index].append(pixels[pixel_index])

        # get the new average for each cluster
        for cluster_index in range(K):
            r_av = average_pixels(clusters[cluster_index], 0)
            g_av = average_pixels(clusters[cluster_index], 1)
            b_av = average_pixels(clusters[cluster_index], 2)

            # update the centroid's values
            centroids[cluster_index][0] = r_av
            centroids[cluster_index][1] = g_av
            centroids[cluster_index][2] = b_av

        # increment count
        iter_count += 1

    # complete the function
    print(f"Iterations: {iter_count}")

    return centroids, cluster_list

def main():
    print()

    # load the image and convert to rgb format
    pixels, height, width = load_image(IMAGE_FILE)

    # run k-means on the pixels
    centroids, cluster_list = k_means(pixels)

    # quantize the pixel's colors
    quantized_pixels = color_quantization(pixels, centroids, cluster_list)

    quantized_pixels = quantized_pixels.reshape(height, width, 3)
    quantized_pixels = quantized_pixels.astype(np.uint8)
    # rerender the image from the new pixels
    img = Image.fromarray(quantized_pixels)
    img.show()

main()