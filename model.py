import torch
from torch import nn

class Attention3dBlock(nn.Module):
    def __init__(self):
        super(Attention3dBlock, self).__init__()

        self.linear = nn.Sequential(
            nn.Linear(
                in_features=30,
                out_features=30
            ),
            nn.Softmax(dim=2),
        )

    # inputs: batch size * window size(time step) * lstm output dims
    def forward(self, inputs):
        # REMIND: tensor.permute returns a view of the original tensor with its dimensions permuted
        x = inputs.permute(0, 2, 1) # inputs(100, 30, 50) -> x(100, 50, 30)
        x = self.linear(x)
        x_probs = x.permute(0, 2, 1)
        # print(torch.sum(x_probs.item()))
        output = x_probs * inputs
        return output

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

        # REMIND:
        #  before
        #       output = (seq_len, batch, hidden_size)
        #  after batch_first=True
        #       output = (batch, seq_len, hidden_size)
        self.lstm = nn.LSTM(
            batch_first=True,
            input_size=17,
            hidden_size=50,
            num_layers=1
        )
        self.attention = Attention3dBlock()
        self.linear = nn.Sequential(
            nn.Linear(in_features=1500, out_features=50),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(in_features=50, out_features=10),
            nn.ReLU(inplace=True)
        )


        self.handcrafted = nn.Sequential(
            nn.Linear(in_features=34, out_features=10),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2)
        )

        self.output = nn.Sequential(
            nn.Linear(in_features=20, out_features=1)
        )

    # REMIND: for FD004, we get
    #         inputs.shape()=(batch=100, window_width=30, sensors=17)
    #         handcrafted_feature.shape()=(batch=100, 34)
    def forward(self, inputs, handcrafted_feature):
        y = self.handcrafted(handcrafted_feature)
        x, (hn, cn) = self.lstm(inputs)
        x = self.attention(x)
        # flatten
        x = x.reshape(-1, 1500)
        x = self.linear(x)
        out = torch.concat((x, y), dim=1)
        out = self.output(out)
        return out
