from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    activeListings = Listing.objects.filter (isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        #Get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        #user
        usernow = request.user
        #category content
        category_data = Category.objects.get(categoryName = category)
        #create a bid object
        bid = Bid(bid = int(price), user=usernow)
        bid.save()
        #  create a new listing
        newListing = Listing(
            title=title,
            description=description,
            imageurl=imageurl,
            price=bid,
            category=category_data,
            owner = usernow
            )
        #  insert it in our db 
        newListing.save()
        # Redirect to index page
        return HttpResponseRedirect(reverse(index))
    
def displayCategory(request):
    if request.method == "POST":
        formcategory = request.POST['category']
        category = Category.objects.get(categoryName=formcategory)
        activeListings = Listing.objects.filter (isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allCategories
    })

def listing(request, id):
    listingInfo = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingInfo.watchlist.all()
    allComments = Comment.objects.filter(listing=listingInfo)
    isOwner = request.user.username == listingInfo.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingInfo,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })

def closeAuction(request, id):
    listingInfo = Listing.objects.get(pk=id)
    listingInfo.isActive = False
    listingInfo.save()
    isListingInWatchlist = request.user in listingInfo.watchlist.all()
    allComments = Comment.objects.filter(listing=listingInfo)
    isOwner = request.user.username == listingInfo.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingInfo,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update" : True,
        "message": "Congratulations! Your auction is closed"
    })

def addBid(request, id):
    newBid = request.POST['newBid']
    listingInfo = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingInfo.watchlist.all()
    allComments = Comment.objects.filter(listing=listingInfo)
    isOwner = request.user.username == listingInfo.owner.username
    if int(newBid) > listingInfo.price.bid:
        updateBid = Bid(user = request.user, bid=int(newBid))
        updateBid.save()
        listingInfo.price = updateBid
        listingInfo.save()
        return render(request, "auctions/listing.html", {
            "listing": listingInfo,
            "message": "Bid was updated successfully",
            "update": True,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isOwner": isOwner
        })
    else:
         return render(request, "auctions/listing.html", {
            "listing": listingInfo,
            "message": "Bid was failed",
            "update": False,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isOwner": isOwner
        })

def addComment(request, id):
    usernow = request.user
    listingInfo = Listing.objects.get(pk=id)
    message = request.POST['newComment']

    newComment = Comment(
        author = usernow,
        listing = listingInfo,
        message = message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def closed_listings(request):
    closed_listings = Listing.objects.filter(isActive=False)
    return render(request, 'auctions/closed_listings.html', {
        'closed_listings': closed_listings
    })

def watchlist(request):
    usernow = request.user
    listings = usernow.listingWatchlist.all()
    return render(request, "Auctions/watchlist.html", {
        "listings": listings
    })

def removeWatchlist(request,id):
    listingInfo = Listing.objects.get(pk=id)
    usernow = request.user
    listingInfo.watchlist.remove(usernow)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addWatchlist(request,id):
    listingInfo = Listing.objects.get(pk=id)
    usernow = request.user
    listingInfo.watchlist.add(usernow)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
