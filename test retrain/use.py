import retrain, label_image
myargs = ['--image_dir', 'D:/code/flower_neural_network/flower_photos', '--output_graph', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\output_graph.pb', '--intermediate_output_graphs_dir', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\intermediate_out', '--output_labels', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\output_labels.txt', '--summaries_dir',
          'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\summaries', '--bottleneck_dir', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\bottleneck_dir', '--how_many_training_steps', '1000', '--model_dir', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\model_dir']
# retrain.myFunc(myargs)
myargs = ['--graph', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\output_graph.pb', '--labels=D:\\code\\Github\\codes-at-home\\profiles\\asdf\\output_labels.txt', '--input_layer=Mul', '--output_layer=final_result', '--input_mean=128', '--input_std=128', '--image=D:/code/flower_neural_network/flower_photos/sunflowers/40410814_fba3837226_n.jpg']
label_image.myFunc(myargs)
