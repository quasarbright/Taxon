import retrain
myargs = ['--image_dir', 'D:/code/flower_neural_network/flower_photos', '--output_graph', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\output_graph.pb', '--intermediate_output_graphs_dir', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\intermediate_out', '--output_labels', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\output_labels.txt', '--summaries_dir',
          'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\summaries', '--bottleneck_dir', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\bottleneck_dir', '--how_many_training_steps', '1000', '--model_dir', 'D:\\code\\Github\\codes-at-home\\profiles\\asdf\\model_dir']
retrain.myFunc(myargs)
