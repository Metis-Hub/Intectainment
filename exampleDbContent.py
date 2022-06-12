from Intectainment import db
from Intectainment.datamodels import Channel, Category


def setup():
    user = User.query.one()

    for channelConfig in [
        ("Intectainment", "Intectainment ist ein Infotainmentsystem"),
        ("SRZ-III", "Algorithmierung"),
        ("SRZ-IV", "Was weiß denn ich"),
    ]:
        channel = Channel(name=channelConfig[0], description=channelConfig[1])
        channel.owner = user
        db.session.add(channel)

    intectainment = Channel.query.filter_by(name="Intectainment").first()
    [
        Post.new(intectainment.id, content, user)
        for content in [
            f"# Post {i}\n\nEs war einmal vor langer, langer Zeit"
            for i in range(0, 100)
        ]
    ]

    for i in range(100):
        channel = Channel(
            name=f"Kanal{i}",
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
        )
        channel.owner = user
        db.session.add(channel)

    for category in [
        "Python",
        "Flask",
        "Java",
        "Infotainment",
        "Informationsübertragung",
        "CSS",
        "JavaScript",
        "Markdown",
    ]:
        db.session.add(Category(name=category))

    db.session.commit()
