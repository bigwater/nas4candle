import tensorflow as tf

from nas4candle.nasapi.search.nas.model.space.block import Block
from nas4candle.nasapi.search.nas.model.space.cell import Cell
from nas4candle.nasapi.search.nas.model.space.node import (ConstantNode, MirrorNode,
                                                   VariableNode)
from nas4candle.nasapi.search.nas.model.space.op.basic import Connect, Tensor, AddByPadding
from nas4candle.nasapi.search.nas.model.space.op.op1d import (Concatenate, Dense,
                                                      Dropout, Identity,
                                                      dropout_ops)
from nas4candle.nasapi.search.nas.model.space.structure import KerasStructure

def set_cell_output_add(cell):
    addNode = ConstantNode(name='Merging')
    addNode.set_op(AddByPadding(cell.graph, addNode, cell.get_blocks_output()))
    cell.set_outputs(node=addNode)

def create_cell_1(input_nodes):
    """Create a cell with convolution.

    Args:
        input_nodes (list(Node)): a list of input_nodes for this cell.

    Returns:
        Cell: the corresponding cell.
    """
    cell = Cell(input_nodes)

    input_dose1 = input_nodes[0]
    input_rnaseq = input_nodes[1]
    input_drug1descriptor = input_nodes[2]
    input_drug1fingerprints = input_nodes[3]

    def create_block_3_nodes(input_node):

        # first node of block
        n1 = ConstantNode(op=Dense(1000, tf.nn.relu), name='N1')
        cell.graph.add_edge(input_node, n1) # fixed input of current block

        # second node of block
        n2 = ConstantNode(op=Dense(1000, tf.nn.relu), name='N2')

        # third node of the block
        n3 = ConstantNode(op=Dense(1000, tf.nn.relu), name='N3')

        block = Block()
        block.add_node(n1)
        block.add_node(n2)
        block.add_node(n3)

        block.add_edge(n1, n2)
        block.add_edge(n2, n3)
        return block, (n1, n2, n3)

    # BLOCK FOR: dose1
    n = ConstantNode(op=Identity(), name='N1', )
    cell.graph.add_edge(input_dose1, n)
    block0 = Block()
    block0.add_node(n)
    cell.add_block(block0)


    # BLOCK FOR: rnaseq
    block3, _ = create_block_3_nodes(input_rnaseq)
    cell.add_block(block3)

    # BLOCK FOR: drug1.descriptor
    block4, _ = create_block_3_nodes(input_drug1descriptor)
    cell.add_block(block4)

    # BLOCK FOR: drug1.fingerprints
    block5, _ = create_block_3_nodes(input_drug1fingerprints)
    cell.add_block(block5)

    # set_cell_output_add(cell)
    cell.set_outputs()
    return cell

def create_mlp_block(cell, input_node):
        block = Block()

        # first node of block
        n1 = ConstantNode(op=Dense(1000, tf.nn.relu), name='N1')
        cell.graph.add_edge(input_node, n1) # fixed input of current block
        block.add_node(n1)

        # second node of block
        n2 = ConstantNode(op=Dense(1000, tf.nn.relu), name='N2')
        block.add_node(n2)

        addNode1 = ConstantNode(name='Merging')
        addNode1.set_op(AddByPadding()) # edge created here
        block.add_node(addNode1)

        block.add_edge(n1, n2)
        block.add_edge(n2, addNode1)
        block.add_edge(n1, addNode1) # residual connection

        n3 = ConstantNode(op=Dense(1000, tf.nn.relu), name='N3')
        block.add_node(n3)

        block.add_edge(addNode1, n3)

        addNode2 = ConstantNode(name='Merging')
        addNode2.set_op(AddByPadding()) # edge created here
        block.add_node(addNode2)

        block.add_edge(n3, addNode2)
        block.add_edge(addNode1, addNode2)

        cell.add_block(block)
        return n1


def create_structure(input_shape=[(2,) for _ in range(4)], output_shape=(1,), num_cell=8, *args, **kwargs):

    network = KerasStructure(input_shape, output_shape) #, output_op=AddByPadding)
    input_nodes = network.input_nodes
    print('input_nodes: ', input_nodes)

    # CELL 1
    cell1 = create_cell_1(input_nodes)
    network.add_cell(cell1)

    # # CELL Middle
    # inputs_skipco = [input_nodes, input_nodes[0], input_nodes[1], input_nodes[2], cell1.output]
    pred_cell = cell1


    # CELL LAST
    cell_last = Cell([pred_cell.output])
    first_node = create_mlp_block(cell_last, pred_cell.output)
    set_cell_output_add(cell_last)

    network.add_cell(cell_last)


    return network

def test_create_structure():
    from random import random, seed
    from nas4candle.nasapi.search.nas.model.space.structure import KerasStructure
    from nas4candle.nasapi.core.model_utils import number_parameters
    from tensorflow.keras.utils import plot_model
    import tensorflow as tf
    # seed(10)
    shapes = [
        (1, ),
        (942, ),
        (5270, ),
        (2048, )
    ]
    structure = create_structure(shapes, (1,))
    assert type(structure) is KerasStructure

    ops = [random() for i in range(structure.num_nodes)]

    print('num ops: ', len(ops))
    print(ops)
    structure.set_ops(ops)
    structure.draw_graphviz('uno_mlp_1.dot')

    model = structure.create_model()
    print('depth: ', structure.depth)
    # model_json = model.to_json()
    # with open('model.json', 'w') as f:
    #     f.write(model_json)
    model = structure.create_model()
    plot_model(model, to_file='uno_mlp_1.png', show_shapes=True)

    # import numpy as np
    # x0 = np.zeros((1, *shapes[0]))
    # x1 = np.zeros((1, *shapes[1]))
    # x2 = np.zeros((1, *shapes[2]))
    # inpts = [x0, x1, x2]
    # y = model.predict(inpts)


    # for x in inpts:
    #     print(f'shape(x): {np.shape(x)}')
    # print(f'shape(y): {np.shape(y)}')

    # total_parameters = number_parameters()
    # print('total_parameters: ', total_parameters)

    model.summary()
    # assert np.shape(y) == (1, 1), f'Wrong output shape {np.shape(y)} should be {(1, 1)}'

if __name__ == '__main__':
    test_create_structure()
